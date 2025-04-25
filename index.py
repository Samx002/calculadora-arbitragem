import streamlit as st
import requests

API_KEY = "809d93f325b63e147dd9c119d8cadbae"  # 🔑 Coloque sua API key aqui
SPORT = "soccer_brazil_campeonato"              # Outros possíveis: mma, boxing...
REGION = "br"
MARKET = "h2h"
BOOKMAKERS = ["bet365", "pinnacle", "1xbet"]

def buscar_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKET,
        "oddsFormat": "decimal",
        "bookmakers": ",".join(BOOKMAKERS)
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    return response.json()

def calcular_arbitragem(odd1, odd2):
    inv_total = (1 / odd1) + (1 / odd2)
    if inv_total < 1:
        lucro = (1 - inv_total) * 100
        return True, lucro
    return False, 0

def calcular_apostas(odd1, odd2, investimento):
    aposta1 = investimento / (1 + (odd1 / odd2))
    aposta2 = investimento - aposta1
    retorno = round(aposta1 * odd1, 2)
    return round(aposta1, 2), round(aposta2, 2), retorno

def main():
    st.set_page_config(page_title="Calculadora de Arbitragem", layout="wide")
    st.title("🎯 Calculadora de Arbitragem entre Casas de Apostas")
    investimento = st.number_input("💰 Valor total a investir (R$)", value=100.0, step=10.0)

    with st.spinner("Buscando odds..."):
        eventos = buscar_odds()

    if not eventos:
        st.warning("⚠️ Não foi possível buscar os dados da API.")
        return

    encontrados = 0

    for evento in eventos:
        odds_encontradas = {}

        for casa in evento["bookmakers"]:
            mercado = casa["markets"][0]
            for i, outcome in enumerate(mercado["outcomes"]):
                if i > 1:
                    continue
                nome = outcome["name"]
                if nome not in odds_encontradas or outcome["price"] > odds_encontradas[nome]["odd"]:
                    odds_encontradas[nome] = {"odd": outcome["price"], "casa": casa["title"]}

        if len(odds_encontradas) == 2:
            jogadores = list(odds_encontradas.keys())
            odd1 = odds_encontradas[jogadores[0]]["odd"]
            odd2 = odds_encontradas[jogadores[1]]["odd"]

            arbitragem, lucro = calcular_arbitragem(odd1, odd2)
            if arbitragem:
                encontrados += 1
                aposta1, aposta2, retorno = calcular_apostas(odd1, odd2, investimento)

                with st.expander(f"🎾 {evento['home_team']} vs {evento['away_team']}"):
                    st.markdown(f"✅ **Arbitragem encontrada com lucro de `{lucro:.2f}%`**")
                    st.markdown(f"- **{jogadores[0]}** @ {odd1} na `{odds_encontradas[jogadores[0]]['casa']}`")
                    st.markdown(f"- **{jogadores[1]}** @ {odd2} na `{odds_encontradas[jogadores[1]]['casa']}`")
                    st.markdown(f"**➡️ Aposte:** R$ `{aposta1}` em {jogadores[0]} | R$ `{aposta2}` em {jogadores[1]}")
                    st.markdown(f"**🔁 Retorno garantido:** R$ `{retorno}`")

    if encontrados == 0:
        st.info("Nenhuma oportunidade de arbitragem encontrada no momento.")

if __name__ == "__main__":
    main()
