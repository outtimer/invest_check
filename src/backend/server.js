const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const app = express();

const rootPath = path.join(__dirname, '..');
const dataPath = path.join(rootPath, '..', 'data');
const viewsPath = path.join(rootPath, 'views');
const publicPath = path.join(rootPath, 'public');
const pythonPath = path.join(rootPath, 'python');

app.set('view engine', 'ejs');
app.set('views', viewsPath);
app.use(express.static(publicPath));

function readJson(fileName) {
    const filePath = path.join(dataPath, fileName);
    if (!fs.existsSync(filePath)) return null;
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
        console.error(`Erro ao ler JSON ${filePath}:`, e);
        return null;
    }
}

function collectTickerStructures() {
    const estruturaB3 = readJson('estrutura_b3_completa.json') || {};
    const estruturaIntl = readJson('estrutura_internacional.json') || {};
    const listaGlobal = [];
    const domesticTickers = new Set();
    const internationalTickers = new Set();
    const seen = new Set();

    Object.values(estruturaB3).forEach(subcats => {
        Object.values(subcats).forEach(list => {
            list.forEach(a => {
                const ticker = (a.ticker || '').toUpperCase();
                if (!ticker) return;
                if (!seen.has(ticker)) {
                    listaGlobal.push(ticker);
                    seen.add(ticker);
                }
                domesticTickers.add(ticker);
                domesticTickers.add(ticker.replace(/\.SA$/, ''));
            });
        });
    });

    Object.values(estruturaIntl).forEach(subcats => {
        Object.values(subcats).forEach(list => {
            list.forEach(a => {
                const ticker = (a.ticker || '').toUpperCase();
                if (!ticker) return;
                if (!seen.has(ticker)) {
                    listaGlobal.push(ticker);
                    seen.add(ticker);
                }
                internationalTickers.add(ticker);
                internationalTickers.add(ticker.replace(/\.SA$/, ''));
            });
        });
    });

    return { listaGlobal, domesticTickers, internationalTickers };
}

function normalizeTicker(symbol) {
    let ticker = symbol.toUpperCase().trim();
    if (ticker.includes('.')) return ticker;

    const { domesticTickers, internationalTickers } = collectTickerStructures();
    if (internationalTickers.has(ticker)) return ticker;
    if (domesticTickers.has(`${ticker}.SA`) || domesticTickers.has(ticker)) return `${ticker}.SA`;
    return ticker;
}

function loadTrendData() {
    const dadosNacional = readJson('dados_tendencia_nacional.json') || { acoes: [], ultima_atualizacao: 'Pendente' };
    const dadosBdr = readJson('dados_tendencia_bdr.json') || { bdrs: [], ultima_atualizacao: 'Pendente' };
    const dadosInternacional = readJson('dados_tendencia_internacional.json') || { internacionais: [], ultima_atualizacao: 'Pendente' };
    const ultima = dadosNacional.ultima_atualizacao || dadosBdr.ultima_atualizacao || dadosInternacional.ultima_atualizacao || 'Pendente';

    return {
        acoes: dadosNacional.acoes,
        bdrs: dadosBdr.bdrs,
        internacionais: dadosInternacional.internacionais,
        ultima_atualizacao: ultima
    };
}

// ==========================================================
// ROTA: HOME (Radar de Tendência)
// ==========================================================
app.get('/', (req, res) => {
    const dados = loadTrendData();
    const { listaGlobal } = collectTickerStructures();

    res.render('index', { dados, listaGlobal });
});

// ==========================================================
// ROTA: MINHA CARTEIRA (Watchlist)
// ==========================================================
app.get('/watchlist', (req, res) => {
    const { listaGlobal } = collectTickerStructures();
    const listaComNomes = listaGlobal.map(t => ({ t, n: t }));
    res.render('watchlist', { listaGlobal: listaComNomes });
});

// ==========================================================
// ROTA: DETALHES TÉCNICOS DO ATIVO
// ==========================================================
app.get('/ticker/:simbolo', (req, res) => {
    const simbolo = req.params.simbolo.toUpperCase().trim();
    const ticker = normalizeTicker(simbolo);

    const scriptPath = path.join(pythonPath, 'consulta_ticker.py');
    exec(`python "${scriptPath}" "${ticker}"`, (err, stdout) => {
        if (err) return res.status(404).send('Erro ao consultar ativo.');
        try {
            res.render('detalhes', { ativo: JSON.parse(stdout) });
        } catch (e) {
            res.status(500).send('Erro.');
        }
    });
});

// ==========================================================
// APIS DE PREÇO (YFINANCE)
// ==========================================================

// Preço atual para a tabela consolidada
app.get('/api/preco/:ticker', (req, res) => {
    const ticker = normalizeTicker(req.params.ticker);
    exec(`python -c "import yfinance as yf; print(yf.Ticker('${ticker}').history(period='1d')['Close'].iloc[-1])"`, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: Number(parseFloat(stdout).toFixed(2)) });
    });
});

// Preço histórico para o Modal de Operação
app.get('/api/preco-historico', (req, res) => {
    let { ticker, data } = req.query;
    if (!ticker || !data) return res.json({ preco: 0 });
    const t = normalizeTicker(ticker);
    const cmd = `python -c "import yfinance as yf; d=yf.download('${t}', start='${data}', period='1d', progress=False); print(d['Close'].iloc[0] if not d.empty else 0)"`;
    exec(cmd, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: Number(parseFloat(stdout).toFixed(2)) });
    });
});

function runScanner(scriptName, res) {
    const scriptPath = path.join(pythonPath, scriptName);
    console.log(`Iniciando scanner ${scriptName} via Python...`);
    exec(`python "${scriptPath}"`, (err, stdout, stderr) => {
        if (err) {
            console.error(`Erro no scanner ${scriptName}:`, stderr || err.message);
            return res.status(500).json({ success: false, error: stderr || err.message });
        }
        console.log(`Scanner ${scriptName} finalizado com sucesso.`);
        res.json({ success: true });
    });
}

// ==========================================================
// ROTA DE ATUALIZAÇÃO (SCANNER DE TENDÊNCIA)
// ==========================================================
app.get('/api/update-tendencia', (req, res) => runScanner('scanner_tendencia.py', res));
app.get('/api/update-tendencia-bdr', (req, res) => runScanner('scanner_tendencia_bdr.py', res));
app.get('/api/update-tendencia-internacional', (req, res) => runScanner('scanner_tendencia_internacional.py', res));

// ==========================================================
// INICIALIZAÇÃO
// ==========================================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Terminal Radar Online: http://localhost:${PORT}`);
});
