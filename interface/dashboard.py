import streamlit as st
import pandas as pd
import altair as alt
import time
from datetime import datetime
import psycopg2

# =========================================================
# CONFIG PAGE
# =========================================================

st.set_page_config(
    page_title="AgriData Sénégal",
    page_icon="🌾",
    layout="wide"
)

# =========================================================
# STYLE CSS
# =========================================================

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
    border-right: 1px solid rgba(120,255,120,0.18);
}

section[data-testid="stSidebar"] * {
    color: #f4fff4 !important;
}

.logo {
    font-size: 34px;
    font-weight: 800;
    color: white;
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

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
}

.subtitle {
    color: #c8e6c9;
    font-size: 16px;
    margin-top: 5px;
}

.card {
    background: linear-gradient(
        145deg,
        rgba(20,78,36,0.85),
        rgba(3,28,13,0.9)
    );

    border: 1px solid rgba(143,209,79,0.35);

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
    color: white;
    font-size: 34px;
    font-weight: 800;
}

.card-note {
    color: #b7d8b2;
    font-size: 13px;
}

.section-card {
    background: rgba(3,26,12,0.72);
    border: 1px solid rgba(143,209,79,0.28);
    border-radius: 20px;
    padding: 22px;
    margin-top: 18px;
}

.section-title {
    color: white;
    font-size: 22px;
    font-weight: 800;
}

.section-subtitle {
    color: #bddbb7;
    font-size: 14px;
    margin-top: 5px;
}

.footer {
    text-align: center;
    color: #cfe8c9;
    padding: 28px;
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="logo">
        🌱 AgriData<br><span>Sénégal</span>
    </div>

    <div class="sidebar-small">
        Cultiver l’avenir, ensemble.
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "",
        [
            "🏠 Tableau de bord",
            "🌾 Champs & parcelles",
            "📊 Analyses",
            "🚨 Alertes",
            "🌦️ Prévisions météo",
            "🛠️ Recommandations",
            "📄 Rapports",
            "⚙️ Paramètres"
        ]
    )

    st.markdown("---")

    st.info(
        "Des données précises pour des décisions intelligentes."
    )

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=5)
def load_data():

    try:

        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database="agri",
            user="admin",
            password="admin"
        )

        df = pd.read_sql(
            "SELECT * FROM capteurs ORDER BY timestamp DESC",
            conn
        )

        conn.close()

        return df

    except:
        return pd.DataFrame()

df = load_data()

# =========================================================
# EMPTY DATA
# =========================================================

if df.empty:

    st.warning(
        "⏳ En attente des données... Le pipeline démarre, patientez quelques instants."
    )

    st.stop()

# =========================================================
# PREP DATA
# =========================================================

df["temperature_air"] = df["temperature_sol"] + 2
df["pluie_mm"] = 0
df["rendement"] = 1.0
df["production_t"] = 10000

df["etat"] = df["alerte"].apply(
    lambda x:
    "CRITIQUE"
    if x != "OK"
    else "BON"
)

# =========================================================
# PAGE : TABLEAU DE BORD
# =========================================================

if menu == "🏠 Tableau de bord":

    st.markdown("""
    <div class="main-title">
        Bienvenue Patron 🌿
    </div>

    <div class="subtitle">
        Vue globale des exploitations agricoles.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    champs_critiques = len(
        df[df["etat"] == "CRITIQUE"]
    )

    production_totale = df["production_t"].sum()

    rendement_moyen = df["rendement"].mean()

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                Champs suivis
            </div>

            <div class="card-value">
                {len(df)}
            </div>

            <div class="card-note">
                100% actifs
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k2:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                Champs critiques
            </div>

            <div class="card-value"
            style="color:#ff5c52;">
                {champs_critiques}
            </div>

            <div class="card-note">
                Surveillance requise
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                Production totale
            </div>

            <div class="card-value">
                {production_totale:,.0f} t
            </div>

            <div class="card-note">
                Production globale
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:

        st.markdown(f"""
        <div class="card">
            <div class="card-title">
                Rendement moyen
            </div>

            <div class="card-value">
                {rendement_moyen:.2f}
            </div>

            <div class="card-note">
                Tonnes / hectare
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TABLEAU

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            ÉTAT DES CHAMPS 🌾
        </div>

        <div class="section-subtitle">
            Surveillance intelligente des exploitations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # CHART

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            ALERTES PAR RÉGION 🚨
        </div>
    </div>
    """, unsafe_allow_html=True)

    chart = alt.Chart(df).mark_bar().encode(
        x="region",
        y="humidite_sol",
        color="etat",
        tooltip=["region", "humidite_sol", "temperature_sol"]
    ).properties(
        height=350
    )

    st.altair_chart(
        chart,
        use_container_width=True
    )

# =========================================================
# PAGE : CHAMPS
# =========================================================

elif menu == "🌾 Champs & parcelles":

    st.title("🌾 Champs & parcelles")

    st.dataframe(
        df,
        use_container_width=True
    )

# =========================================================
# PAGE : ANALYSES
# =========================================================

elif menu == "📊 Analyses":

    st.title("📊 Analyses")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌡️ Température du sol")
        st.line_chart(df["temperature_sol"])

    with c2:
        st.subheader("💧 Humidité du sol")
        st.bar_chart(df["humidite_sol"])

# =========================================================
# PAGE : ALERTES
# =========================================================

elif menu == "🚨 Alertes":

    st.title("🚨 Alertes")

    alertes = df[df["etat"] == "CRITIQUE"]

    if alertes.empty:

        st.success(
            "Aucune alerte critique détectée."
        )

    else:

        st.dataframe(
            alertes,
            use_container_width=True
        )

# =========================================================
# PAGE : MÉTÉO
# =========================================================

elif menu == "🌦️ Prévisions météo":

    st.title("🌦️ Prévisions météo")

    c1, c2, c3, c4, c5 = st.columns(5)

    weather = [
        ("Lun", "☀️", "35°C"),
        ("Mar", "🌤️", "34°C"),
        ("Mer", "🌦️", "32°C"),
        ("Jeu", "🌧️", "30°C"),
        ("Ven", "⛅", "31°C"),
    ]

    for col, item in zip(
        [c1, c2, c3, c4, c5],
        weather
    ):

        with col:

            st.markdown(f"""
            <div class="card"
            style="text-align:center;">

                <div class="card-title">
                    {item[0]}
                </div>

                <div style="font-size:38px;">
                    {item[1]}
                </div>

                <div class="card-value"
                style="font-size:24px;">
                    {item[2]}
                </div>

            </div>
            """, unsafe_allow_html=True)

# =========================================================
# PAGE : RECOMMANDATIONS
# =========================================================

elif menu == "🛠️ Recommandations":

    st.title("🛠️ Recommandations")

    st.success(
        "Irrigation recommandée pour les zones sèches."
    )

    st.info(
        "Surveiller les températures élevées."
    )

# =========================================================
# PAGE : RAPPORTS
# =========================================================

elif menu == "📄 Rapports":

    st.title("📄 Rapports")

    st.download_button(
        label="📥 Télécharger CSV",
        data=df.to_csv(index=False),
        file_name="rapport_agri.csv",
        mime="text/csv"
    )

# =========================================================
# PAGE : PARAMÈTRES
# =========================================================

elif menu == "⚙️ Paramètres":

    st.title("⚙️ Paramètres")

    st.toggle("Mode automatique")

    st.slider(
        "Seuil humidité",
        0,
        100,
        20
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
🌱 AgriData Sénégal — Plateforme intelligente agricole
</div>
""", unsafe_allow_html=True)
