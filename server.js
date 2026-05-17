const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static('public'));

// ==========================================================
// ROTA: HOME (Radar de Tendência)
// ==========================================================
app.get('/', (req, res) => {
    const pathT = path.join(__dirname, 'dados_tendencia.json');
    const pathE = path.join(__dirname, 'estrutura_b3_completa.json');
    let dados = { acoes: [], bdrs: [], ultima_atualizacao: "N/A" };
    let listaGlobal = [];

    if (fs.existsSync(pathT)) {
        try { dados = JSON.parse(fs.readFileSync(pathT, 'utf8')); } catch(e) { console.error(e); }
    }
    if (fs.existsSync(pathE)) {
        try {
            const est = JSON.parse(fs.readFileSync(pathE, 'utf8'));
            for (let c in est) for (let s in est[c]) listaGlobal.push(...est[c][s].map(a => a.ticker));
        } catch(e) {}
    }
    res.render('index', { dados, listaGlobal });
});

// ==========================================================
// ROTA: MINHA CARTEIRA (Watchlist)
// ==========================================================
app.get('/watchlist', (req, res) => {
    const pathE = path.join(__dirname, 'estrutura_b3_completa.json');
    let listaGlobal = [];
    if (fs.existsSync(pathE)) {
        try {
            const est = JSON.parse(fs.readFileSync(pathE, 'utf8'));
            for (let cat in est) {
                for (let sub in est[cat]) {
                    est[cat][sub].forEach(a => listaGlobal.push({ t: a.ticker, n: a.nome }));
                }
            }
        } catch(e) {}
    }
    res.render('watchlist', { listaGlobal });
});

// ==========================================================
// ROTA: DETALHES TÉCNICOS DO ATIVO
// ==========================================================
app.get('/ticker/:simbolo', (req, res) => {
    let simbolo = req.params.simbolo.toUpperCase().trim();
    if (!simbolo.includes('.') && simbolo.length <= 6) simbolo += ".SA";
    exec(`python consulta_ticker.py "${simbolo}"`, (err, stdout) => {
        if (err) return res.status(404).send("Erro ao consultar ativo.");
        try { res.render('detalhes', { ativo: JSON.parse(stdout) }); } catch (e) { res.status(500).send("Erro."); }
    });
});

// ==========================================================
// APIS DE PREÇO (YFINANCE)
// ==========================================================

// Preço atual para a tabela consolidada
app.get('/api/preco/:ticker', (req, res) => {
    let ticker = req.params.ticker.toUpperCase().trim();
    if (!ticker.includes('.') && ticker.length <= 6) ticker += ".SA";
    exec(`python -c "import yfinance as yf; print(yf.Ticker('${ticker}').history(period='1d')['Close'].iloc[-1])"`, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: parseFloat(stdout).toFixed(2) });
    });
});

// Preço histórico para o Modal de Operação
app.get('/api/preco-historico', (req, res) => {
    let { ticker, data } = req.query;
    if (!ticker || !data) return res.json({ preco: 0 });
    let t = ticker.toUpperCase().trim();
    if (!t.includes('.') && t.length <= 6) t += ".SA";
    const cmd = `python -c "import yfinance as yf; d=yf.download('${t}', start='${data}', period='1d', progress=False); print(d['Close'].iloc[0] if not d.empty else 0)"`;
    exec(cmd, (err, stdout) => {
        if (err || !stdout.trim()) return res.json({ preco: 0 });
        res.json({ preco: parseFloat(stdout).toFixed(2) });
    });
});

// ==========================================================
// ROTA DE ATUALIZAÇÃO (SCANNER DE TENDÊNCIA)
// ==========================================================
// Esta é a rota que estava faltando e gerando o seu erro GET
app.get('/api/update-tendencia', (req, res) => {
    console.log("Iniciando scanner de tendência via Python...");
    exec(`python scanner_tendencia.py`, (err, stdout, stderr) => {
        if (err) {
            console.error("Erro no Scanner:", stderr);
            return res.status(500).json({ success: false, error: err.message });
        }
        console.log("Scanner finalizado com sucesso.");
        res.json({ success: true });
    });
});

// ==========================================================
// INICIALIZAÇÃO
// ==========================================================
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 Terminal Radar Online: http://localhost:${PORT}`);
});