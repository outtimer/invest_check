import yfinance as yf
import json
import os
import math
from datetime import datetime

OUTPUT_FILE = "dados_tendencia_internacional.json"


def scanner_tendencia_internacional():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(base_dir, "..", "..", "data", "estrutura_internacional.json")
        caminho_saida = os.path.join(base_dir, "..", "..", "data", OUTPUT_FILE)

        if not os.path.exists(caminho_base):
            print("Erro: Arquivo estrutura_internacional.json nao encontrado.")
            return

        with open(caminho_base, 'r', encoding='utf-8') as f:
            estrutura = json.load(f)

        tickers_internacionais = []
        mapa_nomes = {}

        for subcats in estrutura.get('internacionais', {}).values():
            for ativo in subcats:
                ticker = ativo.get('ticker', '').strip().upper()
                if not ticker:
                    continue
                tickers_internacionais.append(ticker)
                mapa_nomes[ticker] = ativo.get('nome', ticker)

        if not tickers_internacionais:
            print("Nenhum ativo internacional encontrado para scanner.")
            return

        print(f"Iniciando Scanner Internacional para {len(tickers_internacionais)} ativos...")
        df = yf.download(tickers_internacionais, period="1y", progress=False, auto_adjust=True)
        precos = df['Close']
        volumes = df['Volume']

        resultados = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "internacionais": []
        }

        for ticker in tickers_internacionais:
            try:
                if ticker not in precos.columns:
                    continue

                h_p = precos[ticker].dropna()
                if len(h_p) < 200:
                    continue

                p_atual = float(h_p.iloc[-1])
                vol_medio = (h_p.tail(20) * volumes[ticker].tail(20)).mean()
                if vol_medio < 1000000:
                    continue

                m200 = float(h_p.tail(200).mean())
                if p_atual <= m200:
                    continue

                tk = yf.Ticker(ticker)
                info = tk.info

                lpa = info.get('trailingEps', 0)
                vpa = info.get('bookValue', 0)
                if not vpa:
                    total_patrimonio = info.get('totalStockholderEquity', 0)
                    shares_outstanding = info.get('sharesOutstanding', 1)
                    vpa = total_patrimonio / shares_outstanding if shares_outstanding > 0 else 0

                preco_graham = math.sqrt(22.5 * lpa * vpa) if (lpa > 0 and vpa > 0) else 0
                margem_liquida = info.get('profitMargins', 0) * 100
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                trailing_pe = info.get('trailingPE', None)
                pb_ratio = info.get('priceToBook', None)
                total_debt = info.get('totalDebt', 0)
                total_equity = info.get('totalStockholderEquity', 1)
                debt_to_equity = (total_debt / total_equity) if total_equity > 0 else 999
                fcf = info.get('freeCashflow', 0)
                current_eps = info.get('trailingEps', 0)
                forward_eps = info.get('forwardEps', 0)
                eps_growth = (((forward_eps - current_eps) / abs(current_eps)) * 100) if current_eps != 0 else 0

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

                forca = round(((p_atual / m200) - 1) * 100, 2)

                resultados['internacionais'].append({
                    'ticker': ticker,
                    'nome': mapa_nomes.get(ticker, 'N/A'),
                    'preco': round(p_atual, 2),
                    'm200': round(m200, 2),
                    'forca': forca,
                    'graham': round(preco_graham, 2),
                    'margem': round(margem_liquida, 2),
                    'roe': round(roe, 2),
                    'pl': round(trailing_pe, 2) if trailing_pe else None,
                    'pvpa': round(pb_ratio, 2) if pb_ratio else None,
                    'divida_equity': round(debt_to_equity, 2),
                    'eps_growth': round(eps_growth, 2),
                    'score_qualidade': score_qualidade
                })

            except Exception:
                continue

        resultados['internacionais'] = sorted(
            resultados['internacionais'],
            key=lambda x: x['forca'],
            reverse=True
        )[:10]

        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)

        print('Sucesso: dados_tendencia_internacional.json gerado com novos filtros de qualidade.')

    except Exception as exc:
        print(f'Erro: {str(exc)}')


if __name__ == '__main__':
    scanner_tendencia_internacional()
