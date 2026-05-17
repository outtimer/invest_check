# API e Rotas

Este documento descreve as rotas HTTP expostas pelo backend e os dados esperados em cada endpoint.

## Rotas públicas

### GET `/`

- Renderiza o dashboard de tendências.
- Usa `dados_tendencia.json` e `estrutura_b3_completa.json`.

### GET `/watchlist`

- Renderiza a página de carteira.
- Usa `estrutura_b3_completa.json` para preencher as opções de ticker.

### GET `/ticker/:simbolo`

- Renderiza a página de detalhes de um ativo.
- O servidor chama `consulta_ticker.py` com o ticker informado.
- Se o ticker não tiver sufixo, o servidor adiciona `.SA` automaticamente.
- O Python retorna JSON com os indicadores.

### GET `/api/preco/:ticker`

- Retorna o preço atual do ticker.
- Exemplo de resposta:

```json
{ "preco": 12.34 }
```

### GET `/api/preco-historico`

- Parâmetros de query:
  - `ticker` - símbolo do ativo
  - `data` - data no formato `YYYY-MM-DD`
- Retorna o preço do ativo naquela data.
- Exemplo de URL:

```
/api/preco-historico?ticker=PETR4&data=2026-04-01
```

- Exemplo de resposta:

```json
{ "preco": 13.50 }
```

### GET `/api/update-tendencia`

- Executa o scanner de tendência Python `scanner_tendencia.py`.
- Atualiza o arquivo `dados_tendencia.json`.
- Retorna JSON de sucesso ou erro.

## Observações

- A carteira no frontend (`views/watchlist.ejs`) não depende de API para persistência; ela utiliza `localStorage`.
- A rota `/ticker/:simbolo` faz integração direta com Python para fornecer dados técnicos e de proventos.
