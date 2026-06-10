# Terminal Radar B3

Um projeto híbrido de análise de ativos B3 com Node.js/Express, EJS e Python.

> Documento criado e documentado via IA para registrar arquitetura, fluxo de dados e funcionamento do projeto.

## Resumo rápido

- Dashboard de tendências usando `dados_tendencia.json`.
- Detalhes do ticker via `consulta_ticker.py`.
- Scanner de tendência via `scanner_tendencia.py`.
- Watchlist local armazenada com `localStorage`.
- Documentação técnica completa em `docs/`.

## Visão geral

- Backend: `server.js` com Express e templates EJS.
- Frontend: `views/*.ejs` + CSS em `public/css/`.
- Scripts Python: `consulta_ticker.py` e `scanner_tendencia.py`.
- Dados principais: `estrutura_b3_completa.json` e `dados_tendencia.json`.

## Estrutura do projeto

- `src/backend/server.js` - servidor Express principal
- `package.json` - dependências Node
- `src/python/consulta_ticker.py` - consulta de dados e cálculo de métricas por ticker
- `src/python/scanner_tendencia.py` - construção de radar de ativos em tendência
- `src/python/scanner_dividendos.py` - análises de dividendos
- `src/views/index.ejs` - dashboard de tendências
- `src/views/detalhes.ejs` - página de detalhe de ativo
- `src/views/watchlist.ejs` - carteira local com operações em `localStorage`
- `src/public/css/` - estilos visuais
- `data/` - arquivos de dados JSON do projeto
- `legacy/projeto-node/` - código antigo de exemplo Node.js

## Documentação adicional

- `docs/fluxo.md` - fluxo de dados, rotas e diagrama de arquitetura
- `docs/infra.md` - ambiente, dependências e configuração local
- `docs/api.md` - rotas e contrato das APIs expostas
- `docs/contributing.md` - guia de contribuição e boas práticas
- `docs/roadmap.md` - ideias e prioridades para evolução do projeto
- `docs/testes.md` - como rodar testes locais e pipelines de CI
- Branch `feature/docs` foi criada para esta documentação e está pronta para revisão.
- `CHANGELOG.md` - histórico de alterações
- `requirements.txt` - dependências Python
- `Dockerfile` - build de contêiner Docker
- `docker-compose.yml` - orquestração local via Docker Compose
- `LICENSE` - licença de uso do projeto

## Fluxo de funcionamento

1. O usuário acessa `/`.
   - O servidor lê `dados_tendencia.json` e exibe ações e BDRs em tendência.
   - O servidor também usa `estrutura_b3_completa.json` para montar a lista de busca global.

2. O usuário acessa `/watchlist`.
   - O servidor envia lista de tickers para o frontend.
   - A carteira é gerida no navegador com `localStorage`.

3. O usuário acessa `/ticker/:simbolo`.
   - O servidor executa `consulta_ticker.py` usando `child_process.exec`.
   - O script Python retorna JSON com indicadores e informaçõe,s e o servidor renderiza `views/detalhes.ejs`.

4. O usuário dispara o scanner em `/api/update-tendencia`.
   - O servidor executa `scanner_tendencia.py`.
   - O script gera `dados_tendencia.json` com os top 10 em tendência para ações e BDRs.

5. A carteira usa APIs auxiliares:
   - `/api/preco/:ticker` - retorna preço atual via `yfinance`.
   - `/api/preco-historico` - retorna preço em data específica.

## Componentes principais

### `server.js`
- Configura o Express e a view engine EJS.
- Serve arquivos estáticos.
- Define rotas principais e APIs.
- Executa scripts Python para dados dinâmicos.

### `consulta_ticker.py`
- Busca histórico e `info` do ticker com `yfinance`.
- Calcula:
  - preço atual
  - `m200`, `max_200`, `min_200`
  - `preco_graham`
  - `stop` técnico
  - `beta`
  - `margem_liquida`
  - `dy` em 12 meses
  - lista de proventos
- Traduz o resumo da empresa para português com `deep_translator`.

### `scanner_tendencia.py`
- Lê `estrutura_b3_completa.json`.
- Faz download de 1 ano de preços com `yfinance`.
- Filtra por:
  - preço acima da média 200 dias
  - volume médio relevante
  - margem positiva para ações
- Produz `dados_tendencia.json`.

## Como rodar

1. Instale dependências Node:

```bash
npm install
```

2. Garanta que o Python esteja disponível e tenha as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

3. Execute o servidor:

```bash
node src/backend/server.js
```

4. Acesse:

- `http://localhost:3000/`
- `http://localhost:3000/watchlist`

## Testes

- Para rodar os testes Playwright localmente, execute:

```bash
npm test
```

- A documentação de testes está em `docs/testes.md`.

## Rodando com Docker

1. Construa a imagem:

```bash
docker build -t terminal-radar-b3 .
```

2. Execute o contêiner:

```bash
docker run -p 3000:3000 terminal-radar-b3
```

Ou com Docker Compose:

```bash
docker compose up --build
```

## Testes

- Para rodar os testes Playwright localmente, execute:

```bash
npm test
```

- O Playwright iniciará o servidor automaticamente para testar a aplicação local.
- A documentação de testes está em `docs/testes.md`.

## Observações

- A carteira em `watchlist.ejs` não persiste no servidor; usa `localStorage` no navegador.
- O backend depende de chamadas Python via `exec`, portanto é necessário ambiente Python compatível.
- Este documento serve como guia de referência e pode ser adicionado ao repositório GitHub para apresentar a arquitetura.
- Está disponível uma pipeline de CI em `.github/workflows/ci.yml` para verificar instalação e sintaxe de Node e Python.

## Autoria e contexto

- Documento gerado via IA (GitHub Copilot / Raptor mini).
- O projeto atualmente combina Node.js, Express, EJS e Python para análise de ativos B3.
