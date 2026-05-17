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

// ==========================================================
// ROTA: HOME (Radar de Tendência)
// ==========================================================
app.get('/', (req, res) => {
    const dados = readJson('dados_tendencia.json') || { acoes: [], bdrs: [], ultima_atualizacao: 'N/A' };
    const estrutura = readJson('estrutura_b3_completa.json') || {};
    const listaGlobal = [];

    Object.values(estrutura).forEach(subcats => {
        Object.values(subcats).forEach(list => {
            listaGlobal.push(...list.map(a => a.ticker));
        });
    });

    res.render('index', { dados, listaGlobal });
});

// ==========================================================
// ROTA: MINHA CARTEIRA (Watchlist)
// ==========================================================
app.get('/watchlist', (req, res) => {
    const estrutura = readJson('estrutura_b3_completa.json') || {};
    const listaGlobal = [];

    Object.values(estrutura).forEach(subcats => {
        Object.values(subcats).forEach(list => {
            list.forEach(a => listaGlobal.push({ t: a.ticker, n: a.nome }));
        });
    });

    res.render('watchlist', { listaGlobal });
});

// ==========================================================
// ROTA: DETALHES TÉCNICOS DO ATIVO
// ==========================================================
app.get('/ticker/:simbolo', (req, res) => {
    let simbolo = req.params.simbolo.toUpperCase().trim();
    if (!simbolo.includes('.') && simbolo.length <= 6) simbolo += '.SA';

    const scriptPath = path.join(pythonPath, 'consulta_ticker.py');
    exec(`python "${scriptPath}" "${simbolo}"`, (err, stdout) => {
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
    let ticker = req.params.ticker.toUpperCase().trim();
    if (!ticker.includes('.') && ticker.length <= 6) ticker += '.SA';
    exec(`python -c "import yfinance as yf; print(yf.Ticker('${ticker}').history(period='1d')['Close'].iloc[-1])"`, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: Number(parseFloat(stdout).toFixed(2)) });
    });
});

// Preço histórico para o Modal de Operação
app.get('/api/preco-historico', (req, res) => {
    let { ticker, data } = req.query;
    if (!ticker || !data) return res.json({ preco: 0 });
    let t = ticker.toUpperCase().trim();
    if (!t.includes('.') && t.length <= 6) t += '.SA';
    const cmd = `python -c "import yfinance as yf; d=yf.download('${t}', start='${data}', period='1d', progress=False); print(d['Close'].iloc[0] if not d.empty else 0)"`;
    exec(cmd, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: Number(parseFloat(stdout).toFixed(2)) });
    });
});

// ==========================================================
// ROTA DE ATUALIZAÇÃO (SCANNER DE TENDÊNCIA)
// ==========================================================
app.get('/api/update-tendencia', (req, res) => {
    console.log('Iniciando scanner de tendência via Python...');
    const scriptPath = path.join(pythonPath, 'scanner_tendencia.py');
    exec(`python "${scriptPath}"`, (err, stdout, stderr) => {
        if (err) {
            console.error('Erro no Scanner:', stderr);
            return res.status(500).json({ success: false, error: err.message });
        }
        console.log('Scanner finalizado com sucesso.');
        res.json({ success: true });
    });
});

// ==========================================================
// INICIALIZAÇÃO
// ==========================================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Terminal Radar Online: http://localhost:${PORT}`);
});
