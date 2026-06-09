# Regras de Tendência de Ações

Este documento descreve detalhadamente a lógica usada pelo scanner de tendências em `src/python/scanner_tendencia.py` para escolher as melhores ações.

## 1. Fluxo geral do scanner

O scanner executa os seguintes passos:

1. Carrega a lista de ativos da base `data/estrutura_b3_completa.json`.
2. Separa `ações` e `BDRs` em listas distintas.
3. Baixa 1 ano de histórico de preços e volumes via `yfinance` para todos os tickers.
4. Aplica filtros de liquidez e consistência de preço.
5. Para cada ativo válido, calcula métricas fundamentais e de momentum.
6. Gera um `score_qualidade` baseado em critérios de valor e qualidade.
7. Ordena os resultados e salva em `data/dados_tendencia.json`.

## 2. Filtros de liquidez e momentum inicial

Esses filtros descartam ativos que não têm dados suficientes ou não apresentam interesse para um scanner de tendência.

- `len(h_p) < 200`
  - Verifica se o histórico de preço tem pelo menos 200 registros.
  - Isso garante que a média móvel de 200 dias possa ser calculada com confiança.

- `vol_medio < 1000000`
  - Calcula o volume médio dos últimos 20 dias.
  - A fórmula usada é `(preço * volume)` para cada dia e em seguida a média dos 20 últimos dias.
  - O ativo só segue adiante se tiver liquidez razoável (> 1 milhão).

- `p_atual > m200`
  - O preço atual deve estar acima da média móvel de 200 dias (`m200`).
  - Isso garante que o ativo esteja em tendência de alta de longo prazo.

## 3. Cálculos fundamentais por ativo

Para cada ativo que passa nos filtros iniciais, o scanner consulta `yfinance` novamente e extrai várias métricas de `info`.

### 3.1 Preço de Graham

- `preco_graham = sqrt(22.5 * LPA * VPA)`
- `LPA` vem de `trailingEps`
- `VPA` vem de `bookValue`
- Se `bookValue` não estiver disponível, é calculado como `totalStockholderEquity / sharesOutstanding`
- Este valor serve como referência teórica de preço justo segundo a escola de Benjamin Graham.

### 3.2 Margem líquida

- `margem_liquida = profitMargins * 100`
- É a porcentagem de lucro líquido sobre a receita.
- Usado para excluir empresas com margem negativa ou muito baixa.

### 3.3 ROE (Retorno sobre Patrimônio)

- `roe = returnOnEquity * 100`
- Mede a eficiência da empresa em gerar lucro com o capital próprio.
- Critério de qualidade importante para identificar empresas rentáveis.

### 3.4 Valor de mercado / Lucratividade

- `trailing_pe = trailingPE`
- P/L histórico usado como medida de valuation.
- Empresas com P/L muito alto são consideradas mais caras.

### 3.5 P/VPA

- `pb_ratio = priceToBook`
- Relação entre preço de mercado e valor patrimonial.
- Ajuda a identificar ativos potencialmente subavaliados.

### 3.6 Endividamento

- `debt_to_equity = totalDebt / totalStockholderEquity`
- Mede o grau de alavancagem financeira.
- Valores mais baixos indicam capitalização mais conservadora.

### 3.7 Free Cash Flow

- `fcf = freeCashflow`
- Mostra se a empresa gera caixa operacional disponível.
- FCF positivo é sinal de saúde financeira.

### 3.8 Crescimento de EPS

- `current_eps = trailingEps`
- `forward_eps = forwardEps`
- `eps_growth = ((forward_eps - current_eps) / abs(current_eps)) * 100`
- Indica expectativa de crescimento de lucro por ação.

## 4. Score de qualidade

O scanner atribui um score acumulado com base em critérios fundamentais:

- +20 pontos para `ROE > 15%`
- +15 pontos para `P/L < 15`
- +15 pontos para `P/VPA < 1.2`
- +15 pontos para `Debt/Equity < 0.5`
- +15 pontos para `FCF > 0`
- +20 pontos para `EPS Growth > 10%`

Isso cria um ranking de qualidade de 0 a 100.

## 5. Filtros adicionais para ações

Para os ativos classificados como `ações`:

- se `margem_liquida <= 0` e `score_qualidade < 20`, o ativo é descartado
- Esse filtro é mais rigoroso que o usado para BDRs

Ou seja: ações precisam ter lucro operacional e alguma qualidade mínima para entrar no ranking.

## 6. Ordenação final

- `ações` são ordenadas por:
  1. `score_qualidade` (maior primeiro)
  2. `força` (maior primeiro)

- `BDRs` são ordenados apenas por `força`

## 7. Definição de força

- `força = ((preço atual / m200) - 1) * 100`
- Representa a distância do preço em relação à média móvel de 200 dias.
- Quanto maior a força, mais forte é a tendência de alta.

## 8. Resultado gerado

O arquivo final `data/dados_tendencia.json` contém:

- `ultima_atualizacao`
- `acoes` (top 10)
- `bdrs` (top 10)

Cada item traz campos como:
- `ticker`
- `nome`
- `preco`
- `m200`
- `forca`
- `graham`
- `margem`
- `roe`
- `pl`
- `pvpa`
- `divida_equity`
- `eps_growth`
- `score_qualidade`

## 9. Onde o scanner está implementado

- `src/python/scanner_tendencia.py` — lógica de seleção e ranking
- `src/python/consulta_ticker.py` — detalhamento por ticker usado na página de detalhes

## 10. Como o scanner é usado na aplicação

- A rota `/api/update-tendencia` chama `scanner_tendencia.py`
- O dashboard lê `data/dados_tendencia.json`
- A página de detalhe usa `consulta_ticker.py` para informação específica do ticker

---

Esse arquivo descreve o comportamento atual do scanner. Se quiser, posso também incluir sugestões de melhorias e novos filtros a serem adicionados no futuro.