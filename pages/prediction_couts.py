import streamlit as st
import pandas as pd
from models.cost_predictor import CostPredictor
from modules.db_loader import create_database
import plotly.express as px
from datetime import datetime

# Configuration de la page avec métadonnées améliorées
st.set_page_config(
    page_title="Prédiction des Coûts - HealthCost Analytics",
    page_icon="🔮",
    layout="wide",
    menu_items={
        "About": "Module de prédiction des coûts d'assurance santé",
        "Get help": "https://docs.insurecost.com/prediction",
    },
)

# Style personnalisé avec accessibilité améliorée
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
    .prediction-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    .form-group {
        margin-bottom: 1.5rem;
        position: relative;
    }

    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-color);
    }

    .form-help {
        color: var(--text-light);
        font-size: 0.9rem;
        margin-top: 0.25rem;
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

    .message-success {
        background-color: rgba(0, 182, 122, 0.1);
        color: var(--success-color);
        border: 1px solid rgba(0, 182, 122, 0.2);
    }

    .message-error {
        background-color: rgba(228, 30, 49, 0.1);
        color: var(--error-color);
        border: 1px solid rgba(228, 30, 49, 0.2);
    }

    .message-warning {
        background-color: rgba(255, 176, 32, 0.1);
        color: var(--warning-color);
        border: 1px solid rgba(255, 176, 32, 0.2);
    }

    /* Résultats avec accessibilité */
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-top: 2rem;
    }

    .results-title {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }

    .results-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--success-color);
        text-align: center;
        margin: 1.5rem 0;
    }

    /* Facteurs de risque */
    .risk-factors {
        display: grid;
        gap: 1rem;
        margin-top: 1.5rem;
    }

    .risk-factor {
        padding: 1rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .risk-factor-high {
        background-color: rgba(228, 30, 49, 0.1);
        color: var(--error-color);
    }

    .risk-factor-medium {
        background-color: rgba(255, 176, 32, 0.1);
        color: var(--warning-color);
    }

    .risk-factor-low {
        background-color: rgba(0, 182, 122, 0.1);
        color: var(--success-color);
    }

    /* Tooltips accessibles */
    [data-tooltip] {
        position: relative;
        cursor: help;
    }

    [data-tooltip]:before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.5rem 1rem;
        background: var(--text-color);
        color: white;
        border-radius: 4px;
        font-size: 0.875rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 1000;
    }

    [data-tooltip]:hover:before,
    [data-tooltip]:focus:before {
        opacity: 1;
        visibility: visible;
    }

    /* Historique des prédictions */
    .history-container {
        margin-top: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .history-item {
        padding: 1rem;
        border-bottom: 1px solid #E8EEF2;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .history-item:last-child {
        border-bottom: none;
    }

    /* Boutons d'action */
    .action-button {
        background-color: var(--primary-color);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        font-size: 0.9rem;
        transition: background-color 0.2s ease;
    }

    .action-button:hover {
        background-color: var(--secondary-color);
    }

    .action-button:focus {
        outline: 3px solid var(--secondary-color);
        outline-offset: 2px;
    }

    /* Graphique de comparaison */
    .comparison-chart {
        margin-top: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialisation de l'historique des prédictions dans la session
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

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


# Fonction de chargement des données pour la comparaison
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


# Chargement du modèle en cache
@st.cache_resource
def load_model():
    predictor = CostPredictor()
    success = predictor.load_production_model()
    if not success:
        st.markdown(
            """
            <div class="message message-error">
                ⚠️ Erreur lors du chargement du modèle de production. Veuillez vérifier que le modèle a été entraîné.
            </div>
        """,
            unsafe_allow_html=True,
        )
    return predictor


# Fonction pour sauvegarder une prédiction dans l'historique
def save_prediction(input_data, prediction):
    prediction_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input": input_data.to_dict(orient="records")[0],
        "prediction": float(prediction[0]),
    }
    st.session_state.prediction_history.insert(0, prediction_data)
    if (
        len(st.session_state.prediction_history) > 5
    ):  # Garder les 5 dernières prédictions
        st.session_state.prediction_history.pop()


# Fonction de validation des données
def validate_input_data(age, bmi, children, sex, smoker, region):
    """Valide les données d'entrée et retourne un tuple (is_valid, error_messages)"""
    errors = []

    # Validation de l'âge
    if not isinstance(age, (int, float)) or age < 18 or age > 100:
        errors.append("L'âge doit être compris entre 18 et 100 ans")

    # Validation de l'IMC
    if not isinstance(bmi, (int, float)) or bmi < 10 or bmi > 50:
        errors.append("L'IMC doit être compris entre 10 et 50")

    # Validation du nombre d'enfants
    if not isinstance(children, (int)) or children < 0 or children > 10:
        errors.append("Le nombre d'enfants doit être compris entre 0 et 10")

    # Validation du sexe
    if sex not in ["male", "female"]:
        errors.append("Le sexe doit être 'male' ou 'female'")

    # Validation du statut tabagique
    if smoker not in ["yes", "no"]:
        errors.append("Le statut tabagique doit être 'yes' ou 'no'")

    # Validation de la région
    if region not in ["southwest", "southeast", "northwest", "northeast"]:
        errors.append("La région n'est pas valide")

    return len(errors) == 0, errors


# Titre de la page avec accessibilité
st.markdown(
    """
    <div class="prediction-container">
        <h1 role="heading" aria-level="1" style="color: var(--primary-color); font-size: 2.5rem; font-weight: 700; text-align: center; margin-bottom: 0.5rem;">
            🔮 Estimation des Coûts d'Assurance
        </h1>
        <p style="color: var(--text-light); font-size: 1.1rem; text-align: center; max-width: 800px; margin: 0 auto 2rem;">
            Obtenez une estimation précise des coûts d'assurance santé basée sur les caractéristiques individuelles
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Chargement du modèle
predictor = load_model()

# Interface de saisie des données avec accessibilité améliorée
st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
st.markdown(
    """
    <h2 role="heading" aria-level="2" style="color: var(--primary-color); font-size: 1.5rem; font-weight: 600; margin-bottom: 1.5rem;">
        📝 Informations Patient
    </h2>
""",
    unsafe_allow_html=True,
)

# Ajout d'un bouton pour charger un exemple
if st.button(
    "📋 Charger un exemple", help="Remplir le formulaire avec des données d'exemple"
):
    st.session_state.age = 35
    st.session_state.sex = "male"
    st.session_state.bmi = 24.5
    st.session_state.children = 2
    st.session_state.smoker = "no"
    st.session_state.region = "southwest"
    st.markdown(
        """
        <div class="message message-success">
            ✅ Données d'exemple chargées avec succès
        </div>
    """,
        unsafe_allow_html=True,
    )

# Ajout d'un bouton pour réinitialiser le formulaire
if st.button("🔄 Réinitialiser", help="Réinitialiser tous les champs"):
    for key in ["age", "sex", "bmi", "children", "smoker", "region"]:
        if key in st.session_state:
            del st.session_state[key]
    st.markdown(
        """
        <div class="message message-success">
            ✅ Formulaire réinitialisé
        </div>
    """,
        unsafe_allow_html=True,
    )

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="age">🎂 Âge</label>', unsafe_allow_html=True
    )
    age = st.number_input(
        "Âge",
        min_value=18,
        max_value=100,
        value=st.session_state.get("age", 30),
        help="Âge du patient (18-100 ans)",
        key="age",
        label_visibility="collapsed",
    )
    if age < 18 or age > 100:
        st.markdown(
            """
            <div class="message message-error">
                ⚠️ L'âge doit être compris entre 18 et 100 ans
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown(
        "<p class=\"form-help\">L'âge influence significativement les coûts d'assurance</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="sex">👥 Sexe</label>', unsafe_allow_html=True
    )
    sex = st.selectbox(
        "Sexe",
        ["male", "female"],
        index=0 if st.session_state.get("sex", "male") == "male" else 1,
        help="Sexe biologique du patient",
        key="sex",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="bmi">⚖️ IMC</label>', unsafe_allow_html=True
    )
    bmi = st.number_input(
        "IMC",
        min_value=10.0,
        max_value=50.0,
        value=st.session_state.get("bmi", 25.0),
        help="Indice de Masse Corporelle (10-50)",
        key="bmi",
        label_visibility="collapsed",
    )
    if bmi < 10 or bmi > 50:
        st.markdown(
            """
            <div class="message message-error">
                ⚠️ L'IMC doit être compris entre 10 et 50
            </div>
        """,
            unsafe_allow_html=True,
        )
    elif bmi < 18.5:
        st.markdown(
            """
            <div class="message message-warning">
                ⚠️ IMC inférieur à la normale (< 18.5)
            </div>
        """,
            unsafe_allow_html=True,
        )
    elif bmi > 30:
        st.markdown(
            """
            <div class="message message-warning">
                ⚠️ IMC indiquant une obésité (> 30)
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown(
        '<p class="form-help">Un IMC normal se situe entre 18.5 et 25</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="children">👶 Nombre d\'enfants</label>',
        unsafe_allow_html=True,
    )
    children = st.number_input(
        "Nombre d'enfants",
        min_value=0,
        max_value=10,
        value=st.session_state.get("children", 0),
        help="Nombre d'enfants à charge",
        key="children",
        label_visibility="collapsed",
    )
    if children < 0 or children > 10:
        st.markdown(
            """
            <div class="message message-error">
                ⚠️ Le nombre d'enfants doit être compris entre 0 et 10
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="smoker">🚬 Statut tabagique</label>',
        unsafe_allow_html=True,
    )
    smoker = st.selectbox(
        "Statut tabagique",
        ["yes", "no"],
        index=0 if st.session_state.get("smoker", "no") == "yes" else 1,
        help="Le patient est-il fumeur ?",
        key="smoker",
        label_visibility="collapsed",
    )
    if smoker == "yes":
        st.markdown(
            """
            <div class="message message-warning">
                ⚠️ Le tabagisme augmente significativement les coûts d'assurance
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown(
        '<label class="form-label" for="region">🌍 Région</label>',
        unsafe_allow_html=True,
    )
    region = st.selectbox(
        "Région",
        ["southwest", "southeast", "northwest", "northeast"],
        index=["southwest", "southeast", "northwest", "northeast"].index(
            st.session_state.get("region", "southwest")
        ),
        help="Région de résidence",
        key="region",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Bouton de prédiction avec accessibilité
predict_container = st.container()
with predict_container:
    predict_clicked = st.button(
        "💫 Calculer l'Estimation",
        type="primary",
        use_container_width=True,
        key="predict-btn",
    )

if predict_clicked:
    # Validation des données
    is_valid, errors = validate_input_data(age, bmi, children, sex, smoker, region)

    if not is_valid:
        for error in errors:
            st.markdown(
                f"""
                <div class="message message-error">
                    ⚠️ {error}
                </div>
            """,
                unsafe_allow_html=True,
            )
    else:
        try:
            # Animation de chargement avec message accessible
            with st.spinner("Calcul en cours..."):
                # Création du DataFrame pour la prédiction
                input_data = pd.DataFrame(
                    {
                        "age": [age],
                        "sex": [sex],
                        "bmi": [bmi],
                        "nb_children": [children],
                        "smoker": [smoker],
                        "region": [region],
                    }
                )

                # Prédiction
                prediction = predictor.predict(input_data)

                # Sauvegarde dans l'historique
                save_prediction(input_data, prediction)

                # Affichage du résultat avec accessibilité
                st.markdown(
                    """
                    <div class="results-container" role="region" aria-label="Résultats de la prédiction">
                        <h3 class="results-title">
                            💰 Coût d'assurance estimé
                        </h3>
                        <p class="results-value" role="status" aria-live="polite">
                            ${:,.2f}
                        </p>
                        <div style="text-align: center; margin-top: 1rem;">
                            <button class="action-button" onclick="navigator.clipboard.writeText('${:,.2f}')">
                                📋 Copier le montant
                            </button>
                        </div>
                    </div>
                """.format(
                        prediction[0], prediction[0]
                    ),
                    unsafe_allow_html=True,
                )

                # Analyse des facteurs de risque avec accessibilité
                st.markdown(
                    """
                    <div class="risk-factors" role="region" aria-label="Analyse des facteurs de risque">
                        <h3 style="color: var(--primary-color); font-size: 1.5rem; font-weight: 600; margin: 2rem 0 1rem;">
                            📊 Analyse des Facteurs de Risque
                        </h3>
                """,
                    unsafe_allow_html=True,
                )

                # Impact du tabagisme
                smoking_impact = (
                    "augmente significativement"
                    if smoker == "yes"
                    else "n'augmente pas"
                )
                smoking_class = (
                    "risk-factor-high" if smoker == "yes" else "risk-factor-low"
                )
                st.markdown(
                    f"""
                    <div class="risk-factor {smoking_class}" role="status">
                        🚬 Le statut de fumeur {smoking_impact} le coût
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Impact de l'IMC
                bmi_category = (
                    "élevé" if bmi > 30 else "normal" if bmi > 25 else "faible"
                )
                bmi_class = (
                    "risk-factor-high"
                    if bmi > 30
                    else "risk-factor-low" if bmi <= 25 else "risk-factor-medium"
                )
                bmi_icon = "⚠️" if bmi > 30 else "✅" if bmi <= 25 else "⚠️"
                st.markdown(
                    f"""
                    <div class="risk-factor {bmi_class}" role="status">
                        {bmi_icon} L'IMC est {bmi_category} ({bmi:.1f})
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Impact de l'âge
                age_impact = "élevé" if age > 50 else "modéré" if age > 30 else "faible"
                age_class = (
                    "risk-factor-high"
                    if age > 50
                    else "risk-factor-low" if age <= 30 else "risk-factor-medium"
                )
                st.markdown(
                    f"""
                    <div class="risk-factor {age_class}" role="status">
                        🎂 Impact de l'âge : {age_impact}
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Comparaison avec la moyenne
                df = load_data()
                moyenne_generale = df["insurance_cost"].mean()
                difference = prediction[0] - moyenne_generale
                pourcentage = (difference / moyenne_generale) * 100

                comparison_class = (
                    "risk-factor-high"
                    if pourcentage > 20
                    else (
                        "risk-factor-low" if pourcentage < -20 else "risk-factor-medium"
                    )
                )
                st.markdown(
                    f"""
                    <div class="risk-factor {comparison_class}" role="status">
                        📈 {abs(pourcentage):.1f}% {("au-dessus" if pourcentage > 0 else "en-dessous")} de la moyenne générale
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Graphique de comparaison
                st.markdown(
                    """
                    <div class="comparison-chart">
                        <h3 style="color: var(--primary-color); font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">
                            📊 Comparaison avec des profils similaires
                        </h3>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Filtrage des profils similaires
                similar_profiles = df[
                    (df["age"].between(age - 5, age + 5))
                    & (df["bmi"].between(bmi - 2, bmi + 2))
                    & (df["smoking_status"] == smoker)
                ]

                if not similar_profiles.empty:
                    fig = px.box(
                        similar_profiles,
                        y="insurance_cost",
                        title="Distribution des coûts pour des profils similaires",
                        height=400,
                    )

                    # Ajout de la prédiction actuelle
                    fig.add_scatter(
                        y=[prediction[0]],
                        mode="markers",
                        marker=dict(color="red", size=10, symbol="star"),
                        name="Votre estimation",
                        hoverinfo="y",
                    )

                    fig.update_layout(
                        showlegend=True,
                        yaxis_title="Coût d'assurance ($)",
                        plot_bgcolor="white",
                        title_x=0.5,
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(
                        "Pas assez de données pour comparer avec des profils similaires."
                    )

                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.markdown(
                f"""
                <div class="message message-error">
                    ⚠️ Une erreur est survenue lors du calcul : {str(e)}
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.error("Détails techniques de l'erreur :", exception=e)

# Affichage de l'historique des prédictions
if st.session_state.prediction_history:
    st.markdown(
        """
        <div class="history-container">
            <h3 style="color: var(--primary-color); font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">
                📜 Historique des Estimations
            </h3>
    """,
        unsafe_allow_html=True,
    )

    for item in st.session_state.prediction_history:
        st.markdown(
            f"""
            <div class="history-item">
                <div>
                    <strong>{item['timestamp']}</strong><br>
                    Age: {item['input']['age']},
                    IMC: {item['input']['bmi']:.1f},
                    {item['input']['sex'].title()},
                    {item['input']['region'].title()}
                </div>
                <div>
                    <strong>${item['prediction']:,.2f}</strong>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer avec informations complémentaires
st.markdown(
    """
    <footer role="contentinfo" style="margin-top: 3rem; padding: 2rem 0; text-align: center; color: var(--text-light);">
        <p>Les estimations sont basées sur un modèle d'apprentissage automatique entraîné sur des données historiques.</p>
        <p style="margin-top: 0.5rem;">Pour plus d'informations sur la méthodologie, consultez notre <a href="#" style="color: var(--secondary-color);">documentation</a>.</p>
    </footer>
""",
    unsafe_allow_html=True,
)
