import yfinance as yf
import json
import sys
import math
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

def consultar(ticker_nome):
    try:
        tk = yf.Ticker(ticker_nome)
        hist = tk.history(period="1y")
        if hist.empty:
            print(json.dumps({"error": f"Ativo {ticker_nome} nao encontrado"}))
            return

        info = tk.info
        p_atual = float(hist['Close'].iloc[-1])
        
        # Tradução do Resumo
        resumo_original = info.get('longBusinessSummary', 'Resumo indisponivel.')
        try:
            resumo_pt = GoogleTranslator(source='en', target='pt').translate(resumo_original)
        except:
            resumo_pt = resumo_original

        # Fundamentos para Graham
        lpa = info.get('trailingEps', 0)
        vpa = info.get('bookValue', 0)
        if not vpa or vpa == 0:
            total_patrimonio = info.get('totalStockholderEquity', 0)
            shares_outstanding = info.get('sharesOutstanding', 1)
            vpa = total_patrimonio / shares_outstanding if shares_outstanding > 0 else 0

        preco_graham = 0
        if lpa > 0 and vpa > 0:
            preco_graham = math.sqrt(22.5 * lpa * vpa)

        # Novos indicadores de qualidade
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        trailing_pe = info.get('trailingPE', None)
        pb_ratio = info.get('priceToBook', None)
        total_debt = info.get('totalDebt', 0)
        total_equity = info.get('totalStockholderEquity', 1)
        debt_to_equity = (total_debt / total_equity) if total_equity > 0 else None
        fcf = info.get('freeCashflow', 0)
        
        # Crescimento LPA
        current_eps = info.get('trailingEps', 0)
        forward_eps = info.get('forwardEps', 0)
        eps_growth = (((forward_eps - current_eps) / abs(current_eps)) * 100) if current_eps != 0 else 0

        divs = tk.dividends
        um_ano = datetime.now() - timedelta(days=365)
        divs_12m = divs[divs.index >= um_ano.strftime('%Y-%m-%d')]
        
        resultado = {
            "ticker": ticker_nome,
            "nome": info.get('longName', info.get('shortName', ticker_nome)),
            "setor": info.get('sector', 'N/A'),
            "industria": info.get('industry', 'N/A'),
            "website": info.get('website', '#'),
            "resumo": resumo_pt,
            "preco": round(p_atual, 2),
            "dy": round(((float(divs_12m.sum()) / p_atual) * 100), 2) if p_atual > 0 else 0,
            "m200": round(float(hist['Close'].tail(200).mean()), 2),
            "max_200": round(float(hist['High'].tail(200).max()), 2),
            "min_200": round(float(hist['Low'].tail(200).min()), 2),
            "stop": round(p_atual * 0.93, 2),
            "graham": round(preco_graham, 2),
            "beta": round(info.get('beta', 0), 2),
            "margem_liquida": round(info.get('profitMargins', 0) * 100, 2),
            "lpa": round(lpa, 2),
            "vpa": round(vpa, 2),
            "roe": round(roe, 2),
            "pl": round(trailing_pe, 2) if trailing_pe else None,
            "pvpa": round(pb_ratio, 2) if pb_ratio else None,
            "divida_equity": round(debt_to_equity, 2) if debt_to_equity else None,
            "fcf": fcf if fcf else 0,
            "eps_growth_yoy": round(eps_growth, 2),
            "lista_proventos": [{"data_com": i.strftime('%d/%m/%Y'), "valor": float(v)} for i, v in divs_12m.items()][::-1]
        }
        print(json.dumps(resultado))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        consultar(sys.argv[1])