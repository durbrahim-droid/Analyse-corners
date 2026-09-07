import streamlit as st
import pandas as pd
from scipy.stats import poisson

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Football Predictive AI - Pro", layout="wide", page_icon="⚽")

st.title("⚽ Assistant Autonome & Value Bets (Corners, Fautes, xG)")
st.markdown("---")

# --- BASE DE DONNÉES STATISTIQUES ---
@st.cache_data
def load_team_stats():
    data = {
        "Équipe": ["Real Madrid", "Barcelona", "Man City", "Arsenal", "PSG", "Bayern Munich", "Liverpool", "Inter"],
        "Corners_Marques_Dom": [6.8, 6.2, 7.5, 6.4, 5.9, 7.1, 6.9, 5.8],
        "Corners_Concedes_Dom": [3.1, 3.5, 2.8, 3.2, 3.6, 3.0, 3.4, 3.2],
        "Corners_Marques_Ext": [5.2, 5.6, 6.1, 5.1, 5.0, 5.8, 5.5, 4.8],
        "Corners_Concedes_Ext": [4.2, 4.0, 3.5, 3.9, 4.1, 3.8, 4.0, 3.9],
        "xg_Dom": [2.10, 1.95, 2.30, 1.85, 1.80, 2.25, 2.05, 1.75],
        "xg_Ext": [1.65, 1.70, 1.90, 1.55, 1.50, 1.85, 1.70, 1.40],
        "Fautes_Commises": [10.2, 11.5, 9.8, 10.8, 11.0, 9.5, 11.2, 12.1],
        "Fautes_Subies": [12.5, 13.1, 12.0, 11.4, 12.8, 11.9, 11.6, 10.5]
    }
    return pd.DataFrame(data)

df_stats = load_team_stats()

# --- BARRE LATÉRALE ---
st.sidebar.header("🎯 Sélection du Match")
equipes = df_stats["Équipe"].tolist()
home_team = st.sidebar.selectbox("🏠 Équipe Domicile :", equipes, index=0)
away_team = st.sidebar.selectbox("✈️ Équipe Extérieur :", [e for e in equipes if e != home_team], index=1)
bankroll = st.sidebar.number_input("💰 Capital Total (€) :", value=1000, step=50)

# --- CALCULS ---
home_data = df_stats[df_stats["Équipe"] == home_team].iloc[0]
away_data = df_stats[df_stats["Équipe"] == away_team].iloc[0]

st.subheader(f"📊 Analyse Automatique : {home_team} vs {away_team}")

col1, col2, col3, col4 = st.columns(4)
exp_corners_home = (home_data["Corners_Marques_Dom"] + away_data["Corners_Concedes_Ext"]) / 2
exp_corners_away = (away_data["Corners_Marques_Ext"] + home_data["Corners_Concedes_Dom"]) / 2
total_exp_corners = exp_corners_home + exp_corners_away
exp_xg_total = home_data["xg_Dom"] + away_data["xg_Ext"]
exp_fouls_total = home_data["Fautes_Commises"] + away_data["Fautes_Commises"]

col1.metric("Corners Attendus (Total)", f"{total_exp_corners:.2f}")
col2.metric("xG Total Attendu", f"{exp_xg_total:.2f}")
col3.metric("Fautes Attendues", f"{exp_fouls_total:.1f}")
col4.metric("Intensité du Match", "Élevée" if exp_fouls_total > 22 else "Moyenne")

st.markdown("---")
st.header("💡 Détecteur de Value Bets - Corners")

col_c1, col_c2 = st.columns(2)
with col_c1:
    seuil_corners = st.number_input("Seuil Over/Under Corners :", value=9.5, step=1.0)
with col_c2:
    cote_bookmaker = st.number_input(f"Cote Bookmaker Over {seuil_corners} :", value=1.90, step=0.05)

# Calcul Poisson
k_limit = int(seuil_corners)
prob_under = sum([poisson.pmf(i, total_exp_corners) for i in range(k_limit + 1)])
prob_over = 1 - prob_under
fair_odd = 1 / prob_over if prob_over > 0 else 0

# Staking Kelly
b = cote_bookmaker - 1
p = prob_over
q = 1 - p
kelly_fraction = (b * p - q) / b if b > 0 else 0
miste_recommandee = max(0, (kelly_fraction * 0.25) * bankroll)

col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric("Probabilité Estimée", f"{prob_over * 100:.1f}%")
col_res2.metric("Cote Juste Algorithme", f"{fair_odd:.2f}")
col_res3.metric("Mise Recommandée", f"{miste_recommandee:.2f} €")

if cote_bookmaker > fair_odd:
    st.success(f"🔥 **VALUE BET DÉTECTÉE !** La cote bookmaker ({cote_bookmaker}) est supérieure à la cote juste ({fair_odd:.2f}).")
else:
    st.error("❌ Pas de Value Bet sur ce marché.")
