import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime

st.set_page_config(
    page_title="AgriData Sénégal",
    page_icon="🌾",
    layout="wide"
)

# -----------------------------
# STYLE CSS
# -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #123d20 0%, #061b0f 45%, #020d07 100%);
    color: #f4fff4;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #03150a 0%, #0b2d16 55%, #041408 100%);
    border-right: 1px solid rgba(120, 255, 120, 0.18);
}

section[data-testid="stSidebar"] * {
    color: #f4fff4 !important;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #f4fff4;
    margin-bottom: 0;
}

.subtitle {
    color: #c8e6c9;
    font-size: 17px;
    margin-top: 4px;
}

.logo {
    font-size: 34px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0;
}

.logo span {
    color: #8fd14f;
}

.sidebar-small {
    color: #c8e6c9;
    font-size: 14px;
    margin-bottom: 28px;
}

.card {
    background: linear-gradient(145deg, rgba(20, 78, 36, 0.85), rgba(3, 28, 13, 0.9));
    border: 1px solid rgba(143, 209, 79, 0.35);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}

.card-title {
    color: #dff5dc;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.card-value {
    color: #ffffff;
    font-size: 34px;
    font-weight: 800;
}

.card-note {
    color: #b7d8b2;
    font-size: 13px;
}

.section-card {
    background: rgba(3, 26, 12, 0.72);
    border: 1px solid rgba(143, 209, 79, 0.28);
    border-radius: 20px;
    padding: 22px;
    margin-top: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.30);
}

.section-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 4px;
}

.section-subtitle {
    color: #bddbb7;
    font-size: 14px;
    margin-bottom: 18px;
}

.badge-critical {
    background: rgba(210, 62, 48, 0.28);
    color: #ff6b5f;
    border: 1px solid rgba(255, 98, 87, 0.55);
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 800;
    font-size: 12px;
}

.badge-watch {
    background: rgba(230, 185, 45, 0.20);
    color: #ffd24a;
    border: 1px solid rgba(255, 210, 74, 0.55);
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 800;
    font-size: 12px;
}

.badge-good {
    background: rgba(76, 175, 80, 0.18);
    color: #86e070;
    border: 1px solid rgba(134, 224, 112, 0.5);
    border-radius: 10px;
    padding: 6px 10px;
    font-weight: 800;
    font-size: 12px;
}

.footer {
    text-align: center;
    color: #cfe8c9;
    padding: 28px;
    font-size: 16px;
}

div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

.stSelectbox label {
    color: #e8ffe3 !important;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:
    st.markdown("""
    <div class="logo">🌱 AgriData<br><span>Sénégal</span></div>
    <div class="sidebar-small">Cultiver l’avenir, ensemble.</div>
    """, unsafe_allow_html=True)

    st.markdown("### 🏠 Tableau de bord")
    st.markdown("### 🌾 Champs & parcelles")
    st.markdown("### 📊 Analyses")
    st.markdown("### 🚨 Alertes")
    st.markdown("### 🌦️ Prévisions météo")
    st.markdown("### 🛠️ Recommandations")
    st.markdown("### 📄 Rapports")
    st.markdown("### ⚙️ Paramètres")

    st.markdown("---")
    st.info("Des données précises pour des décisions qui nourrissent demain.")


# -----------------------------
# DONNÉES — connexion PostgreSQL
# -----------------------------
import psycopg2

@st.cache_data(ttl=5)
def load_data():
    try:
        conn = psycopg2.connect(
            host="postgres", port=5432,
            database="agri", user="admin", password="admin"
        )
        df = pd.read_sql("SELECT * FROM capteurs ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("⏳ En attente des données... Le pipeline démarre, patientez 3-4 minutes.")
    time.sleep(5)
    st.rerun()

# Renommer les colonnes pour correspondre au reste du dashboard
df = df.rename(columns={
    "region":          "champ",
    "humidite_sol":    "humidite_sol",
    "temperature_sol": "temperature_sol",
    "ph_sol":          "ph_sol",
    "alerte":          "etat_capteur"
})

df["region"] = df["champ"]

# Colonnes manquantes — valeurs par défaut
if "temperature_air"  not in df.columns: df["temperature_air"]  = df["temperature_sol"] + 2
if "pluie_mm"         not in df.columns: df["pluie_mm"]         = 0.0
if "rendement"        not in df.columns: df["rendement"]        = 1.0
if "production_t"     not in df.columns: df["production_t"]     = 10000
if "surface_ha"       not in df.columns: df["surface_ha"]       = 5000
if "culture"          not in df.columns: df["culture"]          = df.get("culture", "Inconnue")

# -----------------------------
# RÈGLES MÉTIER
# -----------------------------

df["risque_secheresse"] = (df["humidite_sol"] < 20) | ((df["pluie_mm"] < 1) & (df["temperature_air"] > 35))
df["probleme_ph"] = (df["ph_sol"] < 5.0) | (df["ph_sol"] > 8.5)
df["stress_chaleur"] = df["temperature_air"] > 35
df["rendement_faible"] = df["rendement"] < 0.8

df["score_risque"] = (
    df["risque_secheresse"].astype(int)
    + df["probleme_ph"].astype(int)
    + df["stress_chaleur"].astype(int)
    + df["rendement_faible"].astype(int)
)

def niveau(score):
    if score >= 3:
        return "CRITIQUE"
    elif score >= 1:
        return "À SURVEILLER"
    return "BON"

df["etat"] = df["score_risque"].apply(niveau)

def probleme(row):
    p = []
    if row["risque_secheresse"]:
        p.append("Sol trop sec + manque de pluie")
    if row["stress_chaleur"]:
        p.append("Température élevée")
    if row["probleme_ph"]:
        p.append("pH du sol déséquilibré")
    if row["rendement_faible"]:
        p.append("Rendement faible")
    return " + ".join(p) if p else "Aucun problème majeur"

df["probleme_principal"] = df.apply(probleme, axis=1)

def action(row):
    a = []
    if row["risque_secheresse"]:
        a.append("Irriguer sous 24h")
    if row["stress_chaleur"]:
        a.append("Paillage + suivi météo")
    if row["probleme_ph"]:
        a.append("Corriger le pH du sol")
    if row["rendement_faible"]:
        a.append("Apport nutriments")
    return " ; ".join(a) if a else "Maintenir pratiques"

df["action_recommandee"] = df.apply(action, axis=1)

# -----------------------------
# HEADER
# -----------------------------

now = datetime.now().strftime("%d %B %Y - %H:%M")

st.markdown("""
<div class="main-title">Bienvenue, Patron 🌿</div>
<div class="subtitle">Voici un aperçu de l’état de vos champs au Sénégal en temps réel.</div>
""", unsafe_allow_html=True)

st.write("")

# -----------------------------
# KPI CARDS
# -----------------------------

champs_critiques = len(df[df["etat"] == "CRITIQUE"])
production_totale = df["production_t"].sum()
rendement_moyen = df["rendement"].mean()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Champs suivis</div>
        <div class="card-value">{len(df)}</div>
        <div class="card-note">100% actifs</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Champs critiques</div>
        <div class="card-value" style="color:#ff5c52;">{champs_critiques}</div>
        <div class="card-note">Nécessitent action</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Production totale</div>
        <div class="card-value">{production_totale:,.0f} t</div>
        <div class="card-note">Suivi global</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Rendement moyen</div>
        <div class="card-value">{rendement_moyen:.2f} t/ha</div>
        <div class="card-note">Sur l’ensemble</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# ÉTAT DES CHAMPS
# -----------------------------

st.markdown("""
<div class="section-card">
<div class="section-title">ÉTAT DES CHAMPS 🌿</div>
<div class="section-subtitle">Vue d’ensemble de tous vos champs avec diagnostic et actions recommandées.</div>
</div>
""", unsafe_allow_html=True)

df_table = df[
    [
        "champ",
        "region",
        "culture",
        "etat",
        "probleme_principal",
        "action_recommandee",
        "rendement",
        "production_t"
    ]
].copy()

st.dataframe(
    df_table,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# DETAIL D'UN CHAMP
# -----------------------------

left, right = st.columns([1.05, 1])

with left:
    st.markdown("""
    <div class="section-card">
    <div class="section-title">DÉTAIL D’UN CHAMP 🌱</div>
    <div class="section-subtitle">Choisissez un champ pour voir son état, ses problèmes et les actions à prévoir.</div>
    </div>
    """, unsafe_allow_html=True)

    champ_choisi = st.selectbox("Choisir un champ :", df["champ"])

    champ = df[df["champ"] == champ_choisi].iloc[0]

    if champ["etat"] == "CRITIQUE":
        badge = '<span class="badge-critical">⚠ CRITIQUE</span>'
    elif champ["etat"] == "À SURVEILLER":
        badge = '<span class="badge-watch">⚠ À SURVEILLER</span>'
    else:
        badge = '<span class="badge-good">✅ BON</span>'

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Nom du champ</div>
        <div class="card-value" style="font-size:28px;">{champ['champ']}</div>
        <div style="margin-top:12px;">{badge}</div>
        <br>
        <div class="card-note"><b>Région :</b> {champ['region']}</div>
        <div class="card-note"><b>Culture :</b> {champ['culture']}</div>
        <div class="card-note"><b>Problème :</b> {champ['probleme_principal']}</div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("💧 Humidité sol", f"{champ['humidite_sol']} %")
    m2.metric("🌡 Température air", f"{champ['temperature_air']} °C")
    m3.metric("🌧 Pluie", f"{champ['pluie_mm']} mm")

    m4, m5, m6 = st.columns(3)
    m4.metric("🧪 pH sol", champ["ph_sol"])
    m5.metric("🌾 Rendement", f"{champ['rendement']} t/ha")
    m6.metric("📦 Production", f"{champ['production_t']:,.0f} t")

    st.subheader("🛠️ Actions recommandées")

    if champ["etat"] == "CRITIQUE":
        st.error(champ["action_recommandee"])
    elif champ["etat"] == "À SURVEILLER":
        st.warning(champ["action_recommandee"])
    else:
        st.success(champ["action_recommandee"])

    st.subheader("🔮 Prévision court terme")

    if champ["risque_secheresse"]:
        st.warning("Sans intervention, risque de baisse du rendement dans les prochains jours.")
    elif champ["probleme_ph"]:
        st.warning("Le pH peut limiter l’absorption des nutriments. Une correction est recommandée.")
    elif champ["stress_chaleur"]:
        st.warning("La chaleur peut augmenter l’évaporation et fragiliser la culture.")
    else:
        st.success("Conditions stables à court terme.")

with right:
    st.markdown("""
    <div class="section-card">
    <div class="section-title">RÉPARTITION DES CHAMPS PAR ÉTAT 🌿</div>
    </div>
    """, unsafe_allow_html=True)

    etat_counts = df["etat"].value_counts().reset_index()
    etat_counts.columns = ["etat", "nombre"]

    chart = alt.Chart(etat_counts).mark_arc(innerRadius=70).encode(
        theta="nombre",
        color=alt.Color(
            "etat",
            scale=alt.Scale(
                domain=["CRITIQUE", "À SURVEILLER", "BON"],
                range=["#ef4444", "#facc15", "#5ecb4f"]
            ),
            legend=alt.Legend(title="État")
        ),
        tooltip=["etat", "nombre"]
    ).properties(height=320)

    st.altair_chart(chart, use_container_width=True)

# -----------------------------
# GRAPHIQUES
# -----------------------------

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div class="section-card">
    <div class="section-title">PRODUCTION PAR CULTURE 🌾</div>
    </div>
    """, unsafe_allow_html=True)

    prod_culture = df.groupby("culture", as_index=False)["production_t"].sum()

    chart_prod = alt.Chart(prod_culture).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("culture", title="Culture"),
        y=alt.Y("production_t", title="Production (t)"),
        color=alt.value("#63c947"),
        tooltip=["culture", "production_t"]
    ).properties(height=300)

    st.altair_chart(chart_prod, use_container_width=True)

with c2:
    st.markdown("""
    <div class="section-card">
    <div class="section-title">SCORE DE RISQUE PAR CHAMP 🚨</div>
    </div>
    """, unsafe_allow_html=True)

    chart_risk = alt.Chart(df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        x=alt.X("champ", sort="-y", title="Champ"),
        y=alt.Y("score_risque", title="Score risque"),
        color=alt.Color(
            "etat",
            scale=alt.Scale(
                domain=["CRITIQUE", "À SURVEILLER", "BON"],
                range=["#ef4444", "#facc15", "#5ecb4f"]
            ),
            legend=None
        ),
        tooltip=["champ", "etat", "score_risque"]
    ).properties(height=300)

    st.altair_chart(chart_risk, use_container_width=True)

# -----------------------------
# PRÉVISIONS MÉTÉO
# -----------------------------

st.markdown("""
<div class="section-card">
<div class="section-title">PRÉVISIONS MÉTÉO — PROCHAINS 5 JOURS 🌦️</div>
<div class="section-subtitle">Prévision simple pour aider à planifier irrigation et surveillance.</div>
</div>
""", unsafe_allow_html=True)

w1, w2, w3, w4, w5 = st.columns(5)

weather = [
    ("Mar 27", "☀️", "36°C", "0 mm"),
    ("Mer 28", "☀️", "35°C", "0 mm"),
    ("Jeu 29", "🌤️", "34°C", "1 mm"),
    ("Ven 30", "🌦️", "32°C", "5 mm"),
    ("Sam 31", "🌧️", "31°C", "8 mm"),
]

for col, item in zip([w1, w2, w3, w4, w5], weather):
    with col:
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div class="card-title">{item[0]}</div>
            <div style="font-size:36px;">{item[1]}</div>
            <div class="card-value" style="font-size:24px;">{item[2]}</div>
            <div class="card-note">{item[3]}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# SYNTHÈSE
# -----------------------------

df_priorite = df.sort_values(by="score_risque", ascending=False)
champ_prioritaire = df_priorite.iloc[0]

st.markdown(f"""
<div class="section-card">
<div class="section-title">🧠 SYNTHÈSE POUR LE PATRON</div>
<div class="section-subtitle">
Le champ prioritaire est <b>{champ_prioritaire['champ']}</b>, situé à <b>{champ_prioritaire['region']}</b>.
Son état est <b>{champ_prioritaire['etat']}</b>.
<br><br>
Action principale recommandée : <b>{champ_prioritaire['action_recommandee']}</b>.
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
🌱 AgriData Sénégal — Cultiver l’avenir, ensemble. 🌱
</div>
""", unsafe_allow_html=True)