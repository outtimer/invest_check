# Infraestrutura e Ambiente

Este documento descreve os requisitos de ambiente e a configuração necessária para rodar o projeto localmente.

## Requisitos mínimos

- Node.js 18+ ou compatível
- npm 9+ (ou compatível com a versão do Node)
- Python 3.10+ (ou versão compatível)
- Internet para `yfinance` e downloads de dados

## Dependências Node

No root do projeto execute:

```bash
npm install
```

As dependências usadas são:

- `express` - servidor web
- `ejs` - templates do frontend

## Dependências Python

Recomenda-se criar um ambiente virtual:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

Em seguida instale:

```bash
pip install yfinance deep-translator
```

Se quiser adicionar ou fixar versões, crie um `requirements.txt` assim:

```txt
yfinance
deep-translator
```

## Executando localmente

Após instalar dependências:

```bash
node src/backend/server.js
```

Abra o navegador em:

- `http://localhost:3000/`
- `http://localhost:3000/watchlist`

## Comandos úteis

- Reiniciar servidor: `Ctrl+C` e `node src/backend/server.js`
- Atualizar scanner de tendência: acionar o botão no dashboard ou chamar `GET /api/update-tendencia`

## Observações de ambiente

- O backend Node.js chama scripts Python via `child_process.exec`, então é necessário que o comando `python` funcione no terminal usado pelo Node.
- Em sistemas Windows, verifique se o Python está no PATH.
- A execução do scanner pode demorar dependendo da quantidade de ativos em `estrutura_b3_completa.json`.
