import yfinance as yf
import json
import os
from datetime import datetime, timedelta

def gerar_json_para_web():
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminho_base = os.path.join(BASE_DIR, "estrutura_b3_completa.json")
        caminho_saida = os.path.join(BASE_DIR, "resultado_web.json")

        if not os.path.exists(caminho_base): return

        with open(caminho_base, 'r', encoding='utf-8') as f:
            estrutura = json.load(f)

        mapa_nomes = {}
        tickers_acoes = []
        tickers_bdrs = []

        for cat, subcats in estrutura.items():
            for sub in subcats.values():
                for ativo in sub:
                    mapa_nomes[ativo['ticker']] = ativo['nome']
                    if cat == "acoes" and not ativo['ticker'].endswith("11.SA"):
                        tickers_acoes.append(ativo['ticker'])
                    elif cat == "bdrs":
                        tickers_bdrs.append(ativo['ticker'])

        dados_finais = {
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acoes": [], "bdrs": [], "ranking_dy": []
        }

        hoje = datetime.now()
        um_ano_atras = hoje - timedelta(days=365)

        # --- ETAPA 1: DOWNLOAD EM LOTE (PREÇO E VOLUME) ---
        print("Baixando dados de mercado para filtragem de liquidez...")
        # Baixamos Close e Volume para o filtro de R$ 1 milhão
        df_raw = yf.download(tickers_acoes + tickers_bdrs, period="1y", progress=False, auto_adjust=True)
        
        precos = df_raw['Close']
        volumes = df_raw['Volume']

        temp_tendencia_acoes = []
        temp_tendencia_bdrs = []
        candidatos_dy = []

        # --- ETAPA 2: PRÉ-PROCESSAMENTO E FILTRAGEM ---
        for t in (tickers_acoes + tickers_bdrs):
            try:
                if t not in precos.columns: continue
                
                h_precos = precos[t].dropna()
                h_volumes = volumes[t].dropna()
                
                if len(h_precos) < 200: continue

                p_atual = float(h_precos.iloc[-1])
                # Média de volume financeiro dos últimos 20 dias (Preço x Volume)
                vol_financeiro_medio = (h_precos.tail(20) * h_volumes.tail(20)).mean()

                # REGRA DE OURO: Liquidez Mínima de R$ 1.000.000,00
                if vol_financeiro_medio < 1000000: continue

                m200 = float(h_precos.tail(200).mean())
                
                item_base = {
                    "ticker": t, "nome": mapa_nomes.get(t, "N/A"),
                    "preco": round(p_atual, 2), "m200": round(m200, 2),
                    "max_200": round(float(h_precos.tail(200).max()), 2),
                    "min_200": round(float(h_precos.tail(200).min()), 2),
                    "stop": round(p_atual * 0.93, 2), "forca": round(((p_atual/m200)-1)*100, 2)
                }

                if p_atual > m200:
                    if t in tickers_acoes: temp_tendencia_acoes.append(item_base)
                    else: temp_tendencia_bdrs.append(item_base)
                
                if t in tickers_acoes: candidatos_dy.append(item_base)
            except: continue

        # --- ETAPA 3: PROCESSAMENTO DETALHADO (DY E PROVENTOS) ---
        # Só gastamos processamento pesado com quem passou no filtro de liquidez
        print("Calculando Dividendos para ativos com liquidez...")
        ranking_dy_final = []
        
        # Ordenamos os candidatos a DY por uma métrica inicial (ex: preço ou ordem alfabética)
        # para processar os mais relevantes primeiro
        for item in candidatos_dy:
            try:
                tk = yf.Ticker(item['ticker'])
                divs = tk.dividends
                divs_12m = divs[divs.index >= um_ano_atras.strftime('%Y-%m-%d')]
                
                if not divs_12m.empty:
                    soma_divs = float(divs_12m.sum())
                    # Cálculo Manual Blindado
                    dy_calc = round((soma_divs / item['preco']) * 100, 2)
                    
                    if 2 < dy_calc < 100: # Filtro de Sanidade
                        item['dy'] = dy_calc
                        item['lista_proventos'] = [
                            {"data_com": i.strftime('%d/%m/%Y'), "valor": float(v)} 
                            for i, v in divs_12m.items()
                        ][::-1]
                        ranking_dy_final.append(item)
            except: continue

        # Montagem Final do JSON
        dados_finais["acoes"] = sorted(temp_tendencia_acoes, key=lambda x: x['forca'], reverse=True)[:10]
        dados_finais["bdrs"] = sorted(temp_tendencia_bdrs, key=lambda x: x['forca'], reverse=True)[:10]
        dados_finais["ranking_dy"] = sorted(ranking_dy_final, key=lambda x: x['dy'], reverse=True)[:10]

        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=4)
        print(f"✅ Scanner Finalizado. {len(candidatos_dy)} ativos passaram no filtro de liquidez.")

    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    gerar_json_para_web()