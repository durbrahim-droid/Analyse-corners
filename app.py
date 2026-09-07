import math
import streamlit as st

st.set_page_config(page_title="Mon Prono Corners IA", layout="wide", page_icon="⚽")

# --- FONCTIONS DE CALCUL ---
def loi_poisson(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def probabilite_cumulee_under(n, lam):
    prob = 0.0
    for k in range(0, int(math.floor(n)) + 1):
        prob += loi_poisson(k, lam)
    return prob

def evaluer_pari(prob, cote_book, capital, kelly_frac):
    if cote_book <= 1.0:
        return "Non", "-", 0.0
    marge = (prob * cote_book) - 1.0
    if marge > 0:
        b = cote_book - 1.0
        f_k = (b * prob - (1.0 - prob)) / b
        mise = max(0.0, capital * f_k * kelly_frac)
        return f"OUI (+{marge*100:.1f}%)", f"{mise:.2f} €", marge
    return "Non", "-", marge

# --- INTERFACE ---
st.title("⚽ Mon Assistant & Calculateur Value Bets Corners")
st.write("Entrez les statistiques du match et les cotes du bookmaker pour obtenir directement le résultat.")

st.sidebar.header("💰 Gestion de Bankroll")
capital = st.sidebar.number_input("Capital Total (€)", value=500.0, step=50.0)
kelly_frac = st.sidebar.slider("Niveau de risque (Kelly)", 0.1, 0.5, 0.25)

st.sidebar.subheader("🌍 Moyennes Ligue")
moy_dom_l = st.sidebar.number_input("Moy. Corners Dom Ligue", value=5.1)
moy_ext_l = st.sidebar.number_input("Moy. Corners Ext Ligue", value=4.3)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Équipe Domicile")
    c_m_d = st.number_input("Corners marqués à Dom", value=6.2)
    c_c_d = st.number_input("Corners concédés à Dom", value=3.5)
    t_c_d = st.number_input("Tirs cadrés/match Dom", value=5.5)

with col2:
    st.subheader("✈️ Équipe Extérieur")
    c_m_e = st.number_input("Corners marqués à Ext", value=4.5)
    c_c_e = st.number_input("Corners concédés à Ext", value=5.8)
    t_c_e = st.number_input("Tirs cadrés/match Ext", value=3.8)

# Calcul lambda
lambda_dom = ((c_m_d * c_c_e) / moy_dom_l) * 0.65 + (t_c_d * 0.92) * 0.35
lambda_ext = ((c_m_e * c_c_d) / moy_ext_l) * 0.65 + (t_c_e * 0.92) * 0.35
lambda_total = lambda_dom + lambda_ext

st.divider()
st.metric("📊 Espérance de corners totales (λ)", f"{lambda_total:.2f} Corners")

st.subheader("🎯 Entrez les cotes du Bookmaker pour analyser les opportunités")

lignes = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5]
donnees = []

for n in lignes:
    prob_u = probabilite_cumulee_under(n, lambda_total)
    prob_o = 1.0 - prob_u
    
    seuil_o = 1.0 / prob_o if prob_o > 0 else 999.0
    seuil_u = 1.0 / prob_u if prob_u > 0 else 999.0

    c1, c2, c3 = st.columns([2, 3, 3])
    with c1:
        st.write(f"**Ligne Over / Under {n}**")
    with c2:
        cote_o = st.number_input(f"Cote OVER {n}", value=1.85 if n == 9.5 else 0.0, step=0.05, key=f"o_{n}")
    with c3:
        cote_u = st.number_input(f"Cote UNDER {n}", value=1.95 if n == 9.5 else 0.0, step=0.05, key=f"u_{n}")

    val_o_txt, mise_o_txt, val_o_num = evaluer_pari(prob_o, cote_o, capital, kelly_frac)
    val_u_txt, mise_u_txt, val_u_num = evaluer_pari(prob_u, cote_u, capital, kelly_frac)

    reco = "Pas de valeur"
    if val_o_num > 0 and val_o_num > val_u_num:
        reco = f"🔥 PARIER OVER ({mise_o_txt})"
    elif val_u_num > 0 and val_u_num > val_o_num:
        reco = f"🔥 PARIER UNDER ({mise_u_txt})"

    donnees.append({
        "Ligne": f"{n}",
        "Proba Over": f"{prob_o*100:.1f}%",
        "Cote Seuil Over": round(seuil_o, 2),
        "Value Over ?": val_o_txt,
        "Proba Under": f"{prob_u*100:.1f}%",
        "Cote Seuil Under": round(seuil_u, 2),
        "Value Under ?": val_u_txt,
        "Recommandation": reco
    })

st.divider()
st.subheader("📋 Résultat de l'analyse")
st.dataframe(donnees, use_container_width=True)
