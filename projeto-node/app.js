const http = require('http');

const server = http.createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.end('Olá DIogo! Seu primeiro servidor Node está rodando sem Apache.');
});

server.listen(3000, '127.0.0.1',() => {
    console.log('Servidor rodando em http://localhost:3000/ - Pressione Ctrl+C para parar. ');
});