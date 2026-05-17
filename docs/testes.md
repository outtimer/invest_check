# Testes

Este documento descreve como executar os testes do projeto localmente e como a automação de CI valida o código.

## Testes Playwright

O projeto inclui testes de fluxo com Playwright em `tests/`, agora focados na própria aplicação local.

### Rodar localmente

1. Instale as dependências Node se ainda não estiverem instaladas:

```bash
npm install
```

2. Instale os navegadores do Playwright:

```bash
npx playwright install --with-deps
```

3. Execute os testes:

```bash
npm test
```

### Estrutura do teste

- `tests/app.spec.ts` contém os testes da aplicação local.
- `tests/ticker.spec.ts` valida a rota `/ticker/:simbolo` para um ativo conhecido.
- `tests/api.spec.ts` valida a API de preço e o modal de nova operação na watchlist.
- `tests/example.spec.ts` permanece disponível como exemplo de Playwright.
- O arquivo de configuração está em `playwright.config.ts`.
- O Playwright iniciará o servidor automaticamente antes de executar os testes.

## Pipeline de CI

O repositório já possui um workflow GitHub Actions em `.github/workflows/ci.yml` que verifica:

- checkout do código
- instalação de dependências Node
- configuração do Python
- verificação de sintaxe de `src/backend/server.js`
- verificação de sintaxe de `consulta_ticker.py` e `scanner_tendencia.py`

Também existe um workflow de Playwright em `.github/workflows/playwright.yml` que:

- instala dependências Node
- instala navegadores do Playwright
- executa os testes com `npx playwright test`
- publica o relatório em `playwright-report/`

## Observações

- Os testes atuais acessam o site `https://playwright.dev/`.
- Se desejar, podemos adaptar os testes para rodar contra a própria aplicação local.
