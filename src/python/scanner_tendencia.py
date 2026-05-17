import yfinance as yf
import json
import os
import math
from datetime import datetime

def scanner_tendencia():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(BASE_DIR, "estrutura_b3_completa.json")
        caminho_saida = os.path.join(BASE_DIR, "dados_tendencia.json")

        if not os.path.exists(caminho_base):
            print("Erro: Arquivo estrutura_b3_completa.json nao encontrado.")
            return

        with open(caminho_base, 'r', encoding='utf-8') as f:
            estrutura = json.load(f)

        tickers_acoes_ref = []
        tickers_bdrs_ref = []
        mapa_nomes = {}

        for cat, subcats in estrutura.items():
            for sub in subcats.values():
                for a in sub:
                    ticker = a['ticker']
                    if ticker.endswith("11.SA"): continue
                    mapa_nomes[ticker] = a['nome']
                    if cat == "acoes": tickers_acoes_ref.append(ticker)
                    elif cat == "bdrs": tickers_bdrs_ref.append(ticker)

        todos_tickers = tickers_acoes_ref + tickers_bdrs_ref
        print(f"Iniciando Scanner para {len(todos_tickers)} ativos...")
        
        df = yf.download(todos_tickers, period="1y", progress=False, auto_adjust=True)
        precos = df['Close']
        volumes = df['Volume']

        resultados = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "acoes": [], 
            "bdrs": []
        }

        for t in todos_tickers:
            try:
                if t not in precos.columns: continue
                h_p = precos[t].dropna()
                if len(h_p) < 200: continue
                
                p_atual = float(h_p.iloc[-1])
                vol_medio = (h_p.tail(20) * volumes[t].tail(20)).mean()
                if vol_medio < 1000000: continue 

                m200 = float(h_p.tail(200).mean())
                
                if p_atual > m200:
                    tk = yf.Ticker(t)
                    info = tk.info
                    
                    # Cálculos para Ações e BDRs
                    lpa = info.get('trailingEps', 0)
                    vpa = info.get('bookValue', 0)
                    preco_graham = math.sqrt(22.5 * lpa * vpa) if (lpa > 0 and vpa > 0) else 0
                    margem = info.get('profitMargins', 0) * 100

                    # Filtro de qualidade apenas para Ações (BDRs costumam ter margens voláteis)
                    if t in tickers_acoes_ref and margem <= 0: continue

                    item = {
                        "ticker": t, "nome": mapa_nomes.get(t, "N/A"),
                        "preco": round(p_atual, 2), "m200": round(m200, 2),
                        "forca": round(((p_atual/m200)-1)*100, 2),
                        "graham": round(preco_graham, 2),
                        "margem": round(margem, 2)
                    }
                    
                    if t in tickers_acoes_ref: resultados["acoes"].append(item)
                    else: resultados["bdrs"].append(item)
            except: continue

        resultados["acoes"] = sorted(resultados["acoes"], key=lambda x: x['forca'], reverse=True)[:10]
        resultados["bdrs"] = sorted(resultados["bdrs"], key=lambda x: x['forca'], reverse=True)[:10]

        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print("Sucesso: dados_tendencia.json gerado.")

    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    scanner_tendencia()