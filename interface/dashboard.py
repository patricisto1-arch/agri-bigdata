import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
import time
from datetime import datetime
from streamlit_option_menu import option_menu

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="AgriData Sénégal",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at top left, #123d20 0%, #061b0f 45%, #020d07 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background:
    linear-gradient(180deg, #03150a 0%, #0b2d16 55%, #041408 100%);
    border-right: 1px solid rgba(120,255,120,0.18);
}

.logo {
    font-size: 38px;
    font-weight: 800;
    color: white;
    line-height: 1.1;
}

.logo span {
    color: #8fd14f;
}

.sidebar-small {
    color: #c8e6c9;
    font-size: 14px;
    margin-top: 10px;
    margin-bottom: 25px;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
}

.subtitle {
    color: #c8e6c9;
    font-size: 17px;
    margin-bottom: 25px;
}

.card {
    background:
    linear-gradient(
        145deg,
        rgba(20,78,36,0.85),
        rgba(3,28,13,0.9)
    );

    border: 1px solid rgba(143,209,79,0.35);

    border-radius: 18px;

    padding: 22px;

    box-shadow:
    0 10px 30px rgba(0,0,0,0.28);
}

.card-title {
    color: #dff5dc;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
}

.card-value {
    color: white;
    font-size: 34px;
    font-weight: 800;
    margin-top: 10px;
}

.card-note {
    color: #b7d8b2;
    font-size: 13px;
    margin-top: 6px;
}

.section-card {
    background: rgba(3,26,12,0.72);

    border:
    1px solid rgba(143,209,79,0.28);

    border-radius: 20px;

    padding: 22px;

    margin-top: 18px;

    box-shadow:
    0 12px 35px rgba(0,0,0,0.30);
}

.section-title {
    color: white;
    font-size: 24px;
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
    padding: 30px;
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
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

if df.empty:

    st.warning(
        "⏳ En attente des données... "
        "Le pipeline démarre, patientez quelques instants."
    )

    time.sleep(5)

    st.rerun()

# =========================================================
# DATA CLEANING
# =========================================================

df = df.rename(columns={
    "region": "champ",
    "humidite_sol": "humidite_sol",
    "temperature_sol": "temperature_sol",
    "ph_sol": "ph_sol",
    "alerte": "etat_capteur"
})

df["region"] = df["champ"]

if "temperature_air" not in df.columns:
    df["temperature_air"] = df["temperature_sol"] + 2

if "pluie_mm" not in df.columns:
    df["pluie_mm"] = 0

if "rendement" not in df.columns:
    df["rendement"] = 1.2

if "production_t" not in df.columns:
    df["production_t"] = 12000

# =========================================================
# BUSINESS RULES
# =========================================================

df["risque_secheresse"] = (
    df["humidite_sol"] < 20
)

df["probleme_ph"] = (
    (df["ph_sol"] < 5.5)
    |
    (df["ph_sol"] > 8)
)

df["stress_chaleur"] = (
    df["temperature_air"] > 35
)

df["score_risque"] = (
    df["risque_secheresse"].astype(int)
    +
    df["probleme_ph"].astype(int)
    +
    df["stress_chaleur"].astype(int)
)

def niveau(score):

    if score >= 2:
        return "CRITIQUE"

    elif score == 1:
        return "À SURVEILLER"

    else:
        return "BON"

df["etat"] = df["score_risque"].apply(niveau)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="logo">
    🌱 AgriData<br>
    <span>Sénégal</span>
    </div>

    <div class="sidebar-small">
    Cultiver l’avenir, ensemble.
    </div>
    """, unsafe_allow_html=True)

    selected = option_menu(

        menu_title=None,

        options=[
            "Dashboard",
            "Champs",
            "Analyses",
            "Alertes",
            "Météo",
            "Rapports",
            "Paramètres"
        ],

        icons=[
            "house-fill",
            "tree-fill",
            "bar-chart-fill",
            "bell-fill",
            "cloud-rain-fill",
            "file-earmark-text-fill",
            "gear-fill"
        ],

        default_index=0,

        styles={

            "container": {
                "padding": "0!important",
                "background-color": "transparent"
            },

            "icon": {
                "color": "#8fd14f",
                "font-size": "18px"
            },

            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "6px",
                "padding": "12px",
                "border-radius": "12px",
                "color": "white"
            },

            "nav-link-selected": {
                "background":
                "linear-gradient(90deg,#1f7a3d,#2ea043)",
                "color": "white",
                "font-weight": "700",
            },
        }
    )

    st.markdown("---")

    st.info(
        "Des données précises pour des décisions intelligentes."
    )

# =========================================================
# DASHBOARD
# =========================================================

if selected == "Dashboard":

    st.markdown("""
    <div class="main-title">
    Bienvenue Patron 🌿
    </div>

    <div class="subtitle">
    Suivi intelligent des exploitations agricoles du Sénégal.
    </div>
    """, unsafe_allow_html=True)

    # KPI

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
            Intervention urgente
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

    # TABLE

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
        ÉTAT DES CHAMPS 🌾
        </div>

        <div class="section-subtitle">
        Diagnostic intelligent des exploitations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # CHARTS

    c1, c2 = st.columns(2)

    with c1:

        etat_counts = (
            df["etat"]
            .value_counts()
            .reset_index()
        )

        etat_counts.columns = [
            "etat",
            "nombre"
        ]

        chart = alt.Chart(
            etat_counts
        ).mark_arc(
            innerRadius=70
        ).encode(
            theta="nombre",
            color=alt.Color(
                "etat",
                scale=alt.Scale(
                    domain=[
                        "CRITIQUE",
                        "À SURVEILLER",
                        "BON"
                    ],

                    range=[
                        "#ef4444",
                        "#facc15",
                        "#5ecb4f"
                    ]
                )
            ),
            tooltip=["etat", "nombre"]
        ).properties(
            height=350
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    with c2:

        chart2 = alt.Chart(df).mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        ).encode(

            x=alt.X(
                "champ",
                sort="-y"
            ),

            y="score_risque",

            color=alt.Color(
                "etat",

                scale=alt.Scale(
                    domain=[
                        "CRITIQUE",
                        "À SURVEILLER",
                        "BON"
                    ],

                    range=[
                        "#ef4444",
                        "#facc15",
                        "#5ecb4f"
                    ]
                )
            ),

            tooltip=[
                "champ",
                "etat",
                "score_risque"
            ]

        ).properties(
            height=350
        )

        st.altair_chart(
            chart2,
            use_container_width=True
        )

# =========================================================
# CHAMPS
# =========================================================

elif selected == "Champs":

    st.title("🌾 Gestion des champs")

    champ = st.selectbox(
        "Choisir un champ",
        df["champ"].unique()
    )

    data = df[df["champ"] == champ]

    st.dataframe(
        data,
        use_container_width=True
    )

# =========================================================
# ANALYSES
# =========================================================

elif selected == "Analyses":

    st.title("📊 Analyses")

    chart = alt.Chart(df).mark_line(
        point=True
    ).encode(

        x="timestamp:T",

        y="temperature_sol:Q",

        color=alt.value("#5ecb4f")

    )

    st.altair_chart(
        chart,
        use_container_width=True
    )

# =========================================================
# ALERTES
# =========================================================

elif selected == "Alertes":

    st.title("🚨 Alertes critiques")

    alertes = df[
        df["etat"] != "BON"
    ]

    st.dataframe(
        alertes,
        use_container_width=True
    )

# =========================================================
# MÉTÉO
# =========================================================

elif selected == "Météo":

    st.title("🌦️ Prévisions météo")

    c1, c2, c3, c4, c5 = st.columns(5)

    meteo = [
        ("Lun", "☀️", "35°C"),
        ("Mar", "🌤️", "34°C"),
        ("Mer", "🌦️", "32°C"),
        ("Jeu", "🌧️", "30°C"),
        ("Ven", "⛅", "31°C"),
    ]

    for col, item in zip(
        [c1,c2,c3,c4,c5],
        meteo
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
# RAPPORTS
# =========================================================

elif selected == "Rapports":

    st.title("📄 Rapports")

    st.download_button(
        label="Télécharger CSV",
        data=df.to_csv(index=False),
        file_name="rapport_agri.csv",
        mime="text/csv"
    )

# =========================================================
# PARAMÈTRES
# =========================================================

elif selected == "Paramètres":

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
