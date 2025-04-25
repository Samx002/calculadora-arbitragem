import streamlit as st
import requests

API_KEY = "809d93f325b63e147dd9c119d8cadbae"  # 🔑 Coloque sua API key aqui
SPORT = "soccer_brazil_campeonato"  # Ex: Brasileirão
REGION = "br"
MARKET = "h2h"  # Mercado head-to-head (1X2)
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

def calcular_arbitragem_3vias(odd1, oddX, odd2):
    inv_total = (1 / odd1) + (1 / oddX) + (1 / odd2)
    if inv_total < 1:
        lucro = (1 - inv_total) * 100
        return True, lucro
    return False, 0

def calcular_apostas_3vias(odd1, oddX, odd2, investimento):
    inv_total = (1 / odd1) + (1 / oddX) + (1 / odd2)
    aposta1 = (investimento / inv_total) / odd1
    apostaX = (investimento / inv_total) / oddX
    aposta2 = (investimento / inv_total) / odd2
    retorno = round(investimento / inv_total, 2)
    return round(aposta1, 2), round(apostaX, 2), round(aposta2, 2), retorno

def main():
    st.set_page_config(page_title="Calculadora de Arbitragem", layout="wide")
    st.title("🎯 Calculadora de Arbitragem 3-Vias (Futebol)")
    investimento = st.number_input("💰 Valor total a investir (R$)", value=100.0, step=10.0)

    with st.spinner("Buscando odds..."):
        eventos = buscar_odds()

    if not eventos:
        st.warning("⚠️ Não foi possível buscar os dados da API.")
        return

    encontrados = 0

    for evento in eventos:
        odds_evento = {}

        for casa in evento["bookmakers"]:
            mercados = casa["markets"]
            for mercado in mercados:
                for outcome in mercado["outcomes"]:
                    nome = outcome["name"]
                    if nome not in odds_evento or outcome["price"] > odds_evento[nome]["odd"]:
                        odds_evento[nome] = {
                            "odd": outcome["price"],
                            "casa": casa["title"]
                        }

        nomes_necessarios = {evento["home_team"], evento["away_team"], "Draw"}

        if nomes_necessarios.issubset(set(odds_evento.keys())):
            odd1 = odds_evento[evento["home_team"]]["odd"]
            oddX = odds_evento["Draw"]["odd"]
            odd2 = odds_evento[evento["away_team"]]["odd"]

            arbitragem, lucro = calcular_arbitragem_3vias(odd1, oddX, odd2)
            if arbitragem:
                encontrados += 1
                aposta1, apostaX, aposta2, retorno = calcular_apostas_3vias(odd1, oddX, odd2, investimento)

                with st.expander(f"⚽ {evento['home_team']} vs {evento['away_team']}"):
                    st.markdown(f"✅ **Arbitragem encontrada com lucro de `{lucro:.2f}%`**")
                    st.markdown(f"- **{evento['home_team']}** @ {odd1} na `{odds_evento[evento['home_team']]['casa']}`")
                    st.markdown(f"- **Empate** @ {oddX} na `{odds_evento['Draw']['casa']}`")
                    st.markdown(f"- **{evento['away_team']}** @ {odd2} na `{odds_evento[evento['away_team']]['casa']}`")
                    st.markdown(f"**➡️ Aposte:** R$ `{aposta1}` no mandante | R$ `{apostaX}` no empate | R$ `{aposta2}` no visitante")
                    st.markdown(f"**🔁 Retorno garantido:** R$ `{retorno}`")

    if encontrados == 0:
        st.info("Nenhuma oportunidade de arbitragem encontrada no momento.")

if __name__ == "__main__":
    main()
