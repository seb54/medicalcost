import streamlit as st
import pandas as pd
import plotly.express as px
from modules.db_loader import create_database

# Configuration de la page avec métadonnées améliorées
st.set_page_config(
    page_title="Analyse Descriptive - HealthCost Analytics",
    page_icon="📊",
    layout="wide",
    menu_items={
        "About": "Module d'analyse descriptive des coûts d'assurance santé",
        "Get help": "https://docs.insurecost.com/analyse",
    },
)

# Style personnalisé pour les graphiques avec accessibilité améliorée
GRAPH_THEME = {
    "bgcolor": "#FFFFFF",
    "font_color": "#2C3345",
    "grid_color": "#E8EEF2",
    "primary_color": "#004B87",
    "secondary_color": "#00A0DF",
    "accent_color": "#00C4B3",
    "colorway": ["#004B87", "#00A0DF", "#00C4B3", "#FFB020", "#E41E31"],
    "pattern_shape_sequence": [
        ".",
        "x",
        "+",
        "-",
        "|",
    ],  # Pour accessibilité daltoniens
}

# Styles CSS pour l'accessibilité
st.markdown(
    """
<style>
    /* Variables globales */
    :root {
        --primary-color: #004B87;
        --secondary-color: #00A0DF;
        --accent-color: #00C4B3;
        --success-color: #00B67A;
        --warning-color: #FFB020;
        --error-color: #E41E31;
        --background-color: #F8FAFB;
        --text-color: #2C3345;
        --text-light: #4A5568;
    }

    /* Amélioration de l'accessibilité */
    .analysis-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }

    /* Support de la navigation au clavier */
    :focus {
        outline: 3px solid var(--secondary-color);
        outline-offset: 2px;
    }

    /* Messages d'état accessibles */
    .message {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .message-warning {
        background-color: rgba(255, 176, 32, 0.1);
        color: var(--warning-color);
        border: 1px solid rgba(255, 176, 32, 0.2);
    }

    /* Graphiques accessibles */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1.5rem 0;
    }

    .chart-title {
        color: var(--primary-color);
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .chart-description {
        color: var(--text-light);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Métriques accessibles */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }

    .metric-label {
        color: var(--text-light);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 600;
    }

    /* Skip to content pour accessibilité */
    .skip-to-content {
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--primary-color);
        color: white;
        padding: 1rem;
        z-index: 100;
        transition: top 0.2s ease;
    }

    .skip-to-content:focus {
        top: 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Skip to content pour accessibilité
st.markdown(
    """
    <a href="#main-content" class="skip-to-content">
        Aller au contenu principal
    </a>
""",
    unsafe_allow_html=True,
)

# Vérification de l'authentification
if "is_authenticated" not in st.session_state or not st.session_state.is_authenticated:
    st.markdown(
        """
        <div class="message message-warning">
            🔒 Veuillez vous connecter pour accéder à cette page
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()


# Fonction de chargement des données
@st.cache_data
def load_data():
    """Charge les données depuis la base"""
    engine = create_database(force_recreate=False)
    with engine.connect() as conn:
        df = pd.read_sql_query(
            """
            SELECT p.*, s.sex_type, sm.smoking_status, r.region_name
            FROM PATIENT p
            JOIN SEX s ON p.id_sex = s.id_sex
            JOIN SMOKING sm ON p.id_smoking_status = sm.id_smoking_status
            JOIN REGION r ON p.id_region = r.id_region
            """,
            conn,
        )
    return df


# Titre de la page avec accessibilité
st.markdown(
    """
    <main id="main-content" role="main" class="analysis-container">
        <h1 role="heading" aria-level="1" style="color: var(--primary-color); font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 0.5rem;">
            📊 Analyse des Coûts Médicaux
        </h1>
        <p style="color: var(--text-light); font-size: 1.1rem; text-align: center; max-width: 800px; margin: 0 auto 2rem;">
            Explorez les tendances et facteurs influençant les coûts d'assurance santé
        </p>
    </main>
""",
    unsafe_allow_html=True,
)

# Chargement des données
df = load_data()

# Statistiques générales avec accessibilité
st.markdown(
    '<section role="region" aria-label="Aperçu financier" class="chart-container">',
    unsafe_allow_html=True,
)
st.subheader("💰 Aperçu Financier Global")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="metric-container">
            <div class="metric-label">Coût Moyen</div>
            <div class="metric-value" role="status" aria-label="Coût moyen">
                ${:,.2f}
            </div>
        </div>
    """.format(
            df["insurance_cost"].mean()
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-container">
            <div class="metric-label">Coût Médian</div>
            <div class="metric-value" role="status" aria-label="Coût médian">
                ${:,.2f}
            </div>
        </div>
    """.format(
            df["insurance_cost"].median()
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-container">
            <div class="metric-label">Coût Maximum</div>
            <div class="metric-value" role="status" aria-label="Coût maximum">
                ${:,.2f}
            </div>
        </div>
    """.format(
            df["insurance_cost"].max()
        ),
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-container">
            <div class="metric-label">Coût Minimum</div>
            <div class="metric-value" role="status" aria-label="Coût minimum">
                ${:,.2f}
            </div>
        </div>
    """.format(
            df["insurance_cost"].min()
        ),
        unsafe_allow_html=True,
    )

st.markdown("</section>", unsafe_allow_html=True)

# Distribution des coûts avec accessibilité
st.markdown(
    '<section role="region" aria-label="Distribution des coûts" class="chart-container">',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <h2 class="chart-title">📈 Distribution des Coûts d'Assurance</h2>
    <p class="chart-description">
        Visualisez la répartition des coûts d'assurance sur l'ensemble de la population
    </p>
""",
    unsafe_allow_html=True,
)

fig = px.histogram(
    df,
    x="insurance_cost",
    nbins=50,
    title="Distribution des Coûts d'Assurance",
    color_discrete_sequence=[GRAPH_THEME["primary_color"]],
)

# Configuration du graphique pour accessibilité
fig.update_layout(
    plot_bgcolor=GRAPH_THEME["bgcolor"],
    paper_bgcolor=GRAPH_THEME["bgcolor"],
    font={"color": GRAPH_THEME["font_color"]},
    title_x=0.5,
    title_font_size=20,
    xaxis=dict(
        title="Coût d'Assurance ($)",
        gridcolor=GRAPH_THEME["grid_color"],
        showline=True,
        linewidth=1,
        linecolor=GRAPH_THEME["grid_color"],
    ),
    yaxis=dict(
        title="Nombre de Patients",
        gridcolor=GRAPH_THEME["grid_color"],
        showline=True,
        linewidth=1,
        linecolor=GRAPH_THEME["grid_color"],
    ),
    bargap=0.1,
)

# Ajout d'une description accessible
fig.update_layout(
    annotations=[
        dict(
            text="Description: Ce graphique montre la distribution des coûts d'assurance. Les barres plus hautes indiquent un plus grand nombre de patients dans cette tranche de coûts.",
            showarrow=False,
            x=0,
            y=-0.2,
            xref="paper",
            yref="paper",
            font=dict(size=12, color=GRAPH_THEME["font_color"]),
        )
    ]
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
st.markdown("</section>", unsafe_allow_html=True)

# Analyse par facteur avec accessibilité
st.markdown(
    '<section role="region" aria-label="Analyse multifactorielle" class="chart-container">',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <h2 class="chart-title">🔍 Analyse Multifactorielle</h2>
    <p class="chart-description">
        Explorez l'impact des différents facteurs sur les coûts d'assurance
    </p>
""",
    unsafe_allow_html=True,
)

factor = st.selectbox(
    "Sélectionnez un facteur d'analyse",
    ["age", "bmi", "nb_children", "sex_type", "smoking_status", "region_name"],
    format_func=lambda x: {
        "age": "Âge",
        "bmi": "IMC",
        "nb_children": "Nombre d'enfants",
        "sex_type": "Sexe",
        "smoking_status": "Statut tabagique",
        "region_name": "Région",
    }[x],
)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.box(
        df,
        x=factor,
        y="insurance_cost",
        title=f"Distribution des Coûts par {factor}",
        color_discrete_sequence=[GRAPH_THEME["secondary_color"]],
    )

    # Configuration pour accessibilité
    fig1.update_layout(
        plot_bgcolor=GRAPH_THEME["bgcolor"],
        paper_bgcolor=GRAPH_THEME["bgcolor"],
        font={"color": GRAPH_THEME["font_color"]},
        title_x=0.5,
        title_font_size=18,
        xaxis=dict(
            gridcolor=GRAPH_THEME["grid_color"],
            showline=True,
            linewidth=1,
            linecolor=GRAPH_THEME["grid_color"],
        ),
        yaxis=dict(
            title="Coût d'Assurance ($)",
            gridcolor=GRAPH_THEME["grid_color"],
            showline=True,
            linewidth=1,
            linecolor=GRAPH_THEME["grid_color"],
        ),
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.violin(
        df,
        x=factor,
        y="insurance_cost",
        title=f"Distribution Détaillée par {factor}",
        color_discrete_sequence=[GRAPH_THEME["accent_color"]],
    )

    # Configuration pour accessibilité
    fig2.update_layout(
        plot_bgcolor=GRAPH_THEME["bgcolor"],
        paper_bgcolor=GRAPH_THEME["bgcolor"],
        font={"color": GRAPH_THEME["font_color"]},
        title_x=0.5,
        title_font_size=18,
        xaxis=dict(
            gridcolor=GRAPH_THEME["grid_color"],
            showline=True,
            linewidth=1,
            linecolor=GRAPH_THEME["grid_color"],
        ),
        yaxis=dict(
            title="Coût d'Assurance ($)",
            gridcolor=GRAPH_THEME["grid_color"],
            showline=True,
            linewidth=1,
            linecolor=GRAPH_THEME["grid_color"],
        ),
    )

    st.plotly_chart(fig2, use_container_width=True)

st.markdown("</section>", unsafe_allow_html=True)

# Analyse des corrélations avec accessibilité
st.markdown(
    '<section role="region" aria-label="Analyse des corrélations" class="chart-container">',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <h2 class="chart-title">🔄 Analyse des Corrélations</h2>
    <p class="chart-description">
        Découvrez les relations entre les différentes variables et leur impact sur les coûts
    </p>
""",
    unsafe_allow_html=True,
)

# Création d'un DataFrame pour l'analyse des variables catégorielles
df_encoded = df.copy()
df_encoded["smoker_encoded"] = (df_encoded["smoking_status"] == "yes").astype(int)
df_encoded["sex_encoded"] = (df_encoded["sex_type"] == "male").astype(int)

# Création de variables dummy pour la région
region_dummies = pd.get_dummies(df_encoded["region_name"], prefix="region")
df_encoded = pd.concat([df_encoded, region_dummies], axis=1)

# Sélection des colonnes pour la matrice de corrélation
correlation_columns = [
    "age",
    "bmi",
    "nb_children",
    "insurance_cost",
    "smoker_encoded",
    "sex_encoded",
] + list(region_dummies.columns)

# Calcul et affichage de la matrice de corrélation
corr_matrix = df_encoded[correlation_columns].corr()

# Renommage des colonnes pour plus de clarté
column_names = {
    "age": "Âge",
    "bmi": "IMC",
    "nb_children": "Nb Enfants",
    "insurance_cost": "Coût Assurance",
    "smoker_encoded": "Fumeur",
    "sex_encoded": "Sexe (H)",
    "region_southwest": "Sud-Ouest",
    "region_southeast": "Sud-Est",
    "region_northwest": "Nord-Ouest",
    "region_northeast": "Nord-Est",
}

corr_matrix_renamed = corr_matrix.rename(columns=column_names, index=column_names)

# Création de la heatmap avec accessibilité
fig = px.imshow(
    corr_matrix_renamed,
    color_continuous_scale=[[0, "#E41E31"], [0.5, "#FFFFFF"], [1, "#00B67A"]],
    aspect="auto",
    title="Matrice de Corrélation",
)

# Configuration pour accessibilité
fig.update_layout(
    title_x=0.5,
    title_font_size=20,
    font={"color": GRAPH_THEME["font_color"]},
    plot_bgcolor=GRAPH_THEME["bgcolor"],
    paper_bgcolor=GRAPH_THEME["bgcolor"],
)

# Ajout d'une description accessible
fig.update_layout(
    annotations=[
        dict(
            text="Description: Cette matrice montre les corrélations entre les différentes variables. Les couleurs plus foncées indiquent des corrélations plus fortes.",
            showarrow=False,
            x=0,
            y=-0.15,
            xref="paper",
            yref="paper",
            font=dict(size=12, color=GRAPH_THEME["font_color"]),
        )
    ]
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</section>", unsafe_allow_html=True)

# Footer avec informations complémentaires
st.markdown(
    """
    <footer role="contentinfo" style="margin-top: 3rem; padding: 2rem 0; text-align: center; color: var(--text-light);">
        <p>Les analyses sont basées sur les données historiques des coûts d'assurance santé.</p>
        <p style="margin-top: 0.5rem;">Pour plus d'informations sur la méthodologie, consultez notre <a href="#" style="color: var(--secondary-color);">documentation</a>.</p>
    </footer>
""",
    unsafe_allow_html=True,
)
