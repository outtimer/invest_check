import yfinance as yf
import json
import os
import math
from datetime import datetime

def scanner_tendencia():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(BASE_DIR, "..", "..", "data", "estrutura_b3_completa.json")
        caminho_saida = os.path.join(BASE_DIR, "..", "..", "data", "dados_tendencia_nacional.json")

        if not os.path.exists(caminho_base):
            print("Erro: Arquivo estrutura_b3_completa.json nao encontrado.")
            return

        with open(caminho_base, 'r', encoding='utf-8') as f:
            estrutura = json.load(f)

        tickers_acoes_ref = []
        mapa_nomes = {}

        for subcats in estrutura.get('acoes', {}).values():
            for a in subcats:
                ticker = a.get('ticker', '').strip().upper()
                if not ticker or ticker.endswith("11.SA"):
                    continue
                mapa_nomes[ticker] = a.get('nome', ticker)
                tickers_acoes_ref.append(ticker)

        if not tickers_acoes_ref:
            print('Nenhum ativo nacional encontrado para scanner.')
            return

        print(f"Iniciando Scanner Nacional para {len(tickers_acoes_ref)} ativos...")
        
        df = yf.download(tickers_acoes_ref, period="1y", progress=False, auto_adjust=True)
        precos = df['Close']
        volumes = df['Volume']

        resultados = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "acoes": []
        }

        for t in tickers_acoes_ref:
            try:
                if t not in precos.columns:
                    continue

                h_p = precos[t].dropna()
                if len(h_p) < 200:
                    continue

                p_atual = float(h_p.iloc[-1])
                vol_medio = (h_p.tail(20) * volumes[t].tail(20)).mean()
                if vol_medio < 1000000:
                    continue

                m200 = float(h_p.tail(200).mean())
                if p_atual <= m200:
                    continue

                tk = yf.Ticker(t)
                info = tk.info

                # ============================================
                # FUNDAMENTOS E CÁLCULOS DE QUALIDADE
                # ============================================

                # 1. Preço de Graham
                lpa = info.get('trailingEps', 0)
                vpa = info.get('bookValue', 0)
                if not vpa or vpa == 0:
                    total_patrimonio = info.get('totalStockholderEquity', 0)
                    shares_outstanding = info.get('sharesOutstanding', 1)
                    vpa = total_patrimonio / shares_outstanding if shares_outstanding > 0 else 0

                preco_graham = math.sqrt(22.5 * lpa * vpa) if (lpa > 0 and vpa > 0) else 0

                # 2. Margens e Rentabilidade
                margem_liquida = info.get('profitMargins', 0) * 100
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0

                # 3. PL (Price to Earnings)
                trailing_pe = info.get('trailingPE', None)

                # 4. P/VPA (Price to Book)
                pb_ratio = info.get('priceToBook', None)

                # 5. Dívida (Debt/Equity)
                total_debt = info.get('totalDebt', 0)
                total_equity = info.get('totalStockholderEquity', 1)
                debt_to_equity = (total_debt / total_equity) if total_equity > 0 else 999

                # 6. Free Cash Flow
                fcf = info.get('freeCashflow', 0)

                # 7. Crescimento LPA (Year over Year)
                current_eps = info.get('trailingEps', 0)
                forward_eps = info.get('forwardEps', 0)
                eps_growth = (((forward_eps - current_eps) / abs(current_eps)) * 100) if current_eps != 0 else 0

                # ============================================
                # FILTROS DE QUALIDADE (Graham + Momentum)
                # ============================================

                score_qualidade = 0
                if roe > 15:
                    score_qualidade += 20
                if trailing_pe and trailing_pe < 15:
                    score_qualidade += 15
                if pb_ratio and pb_ratio < 1.2:
                    score_qualidade += 15
                if debt_to_equity < 0.5:
                    score_qualidade += 15
                if fcf > 0:
                    score_qualidade += 15
                if eps_growth > 10:
                    score_qualidade += 20

                if margem_liquida <= 0 and score_qualidade < 20:
                    continue

                forca = round(((p_atual / m200) - 1) * 100, 2)

                item = {
                    "ticker": t,
                    "nome": mapa_nomes.get(t, "N/A"),
                    "preco": round(p_atual, 2),
                    "m200": round(m200, 2),
                    "forca": forca,
                    "graham": round(preco_graham, 2),
                    "margem": round(margem_liquida, 2),
                    "roe": round(roe, 2),
                    "pl": round(trailing_pe, 2) if trailing_pe else None,
                    "pvpa": round(pb_ratio, 2) if pb_ratio else None,
                    "divida_equity": round(debt_to_equity, 2),
                    "eps_growth": round(eps_growth, 2),
                    "score_qualidade": score_qualidade
                }

                resultados["acoes"].append(item)
            except Exception:
                continue

        resultados["acoes"] = sorted(
            resultados["acoes"], 
            key=lambda x: (x['score_qualidade'], x['forca']), 
            reverse=True
        )[:10]

        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)
        print("Sucesso: dados_tendencia_nacional.json gerado com novos filtros de qualidade.")

    except Exception as exc:
        print(f"Erro: {str(exc)}")

if __name__ == "__main__":
    scanner_tendencia()