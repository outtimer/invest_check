import yfinance as yf
import json
import os
from datetime import datetime, timedelta

def scanner_dividendos():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(BASE_DIR, "estrutura_b3_completa.json")
        caminho_saida = os.path.join(BASE_DIR, "dados_dividendos.json")

        with open(caminho_base, 'r', encoding='utf-8') as f:
            estrutura = json.load(f)

        tickers_acoes = []
        mapa_nomes = {}
        for cat, sub in estrutura.items():
            if cat == "acoes":
                for ativos in sub.values():
                    for a in ativos:
                        tickers_acoes.append(a['ticker'])
                        mapa_nomes[a['ticker']] = a['nome']

        print("Baixando precos para Dividendos...")
        # Baixamos apenas as acoes para o Ranking DY
        df_precos = yf.download(tickers_acoes, period="5d", progress=False)['Close']
        
        ranking_dy = []
        um_ano = datetime.now() - timedelta(days=365)

        for t in tickers_acoes[:150]:
            try:
                tk = yf.Ticker(t)
                divs = tk.dividends
                divs_12m = divs[divs.index >= um_ano.strftime('%Y-%m-%d')]
                
                if not divs_12m.empty:
                    soma = float(divs_12m.sum())
                    if t not in df_precos.columns: continue
                    p_atual = float(df_precos[t].dropna().iloc[-1])
                    dy = round((soma / p_atual) * 100, 2)

                    if 2 < dy < 100 and p_atual > 1.0:
                        ranking_dy.append({
                            "ticker": t, "nome": mapa_nomes.get(t, "N/A"),
                            "dy": dy, "preco": round(p_atual, 2),
                            "lista_proventos": [{"data_com": i.strftime('%d/%m/%Y'), "valor": float(v)} for i, v in divs_12m.items()][::-1]
                        })
            except: continue

    except Exception as e:
        print(f"Erro: {e}")

    resultados = {
        "ranking_dy": sorted(ranking_dy, key=lambda x: x['dy'], reverse=True)[:10]
    }

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print("Sucesso: dados_dividendos.json gerado.")

if __name__ == "__main__":
    scanner_dividendos()