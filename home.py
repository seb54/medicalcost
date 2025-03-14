import streamlit as st
from modules.db_loader import create_database
from modules.auth import verify_user

# Configuration de la page avec métadonnées améliorées
st.set_page_config(
    page_title="InsureCost Analytics - Analyse des Coûts d'Assurance Santé",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "InsureCost Analytics - Version 1.0.0\nDéveloppé avec ❤️ pour l'analyse des coûts d'assurance santé",
        "Report a bug": "mailto:support@insurecost.com",
        "Get help": "https://docs.insurecost.com",
    },
)

# Styles CSS personnalisés avec accessibilité améliorée
st.markdown(
    """
<style>
    /* Variables globales */
    :root {
        --primary-color: #004B87;
        --secondary-color: #00A0DF;
        --accent-color: #00C4B3;
        --background-color: #F8FAFB;
        --text-color: #2C3345;
        --text-light: #4A5568;
        --success-color: #00B67A;
        --error-color: #E41E31;
        --warning-color: #FFB020;
        --neutral-color: #E8EEF2;
        
        /* Espacements */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        
        /* Transitions */
        --transition-fast: 0.2s;
        --transition-normal: 0.3s;
        --transition-slow: 0.5s;
    }
    
    /* Reset et base */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    /* Amélioration de l'accessibilité */
    :focus {
        outline: 3px solid var(--secondary-color);
        outline-offset: 2px;
    }
    
    [role="button"]:focus {
        box-shadow: 0 0 0 3px rgba(0, 160, 223, 0.4);
    }
    
    /* Style général */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }
    
    /* Style du menu avec accessibilité améliorée */
    .css-1d391kg {
        background-color: white;
        padding: var(--spacing-xl) 0;
        border-right: none;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    }
    
    /* En-tête du menu */
    .menu-header {
        text-align: center;
        padding: var(--spacing-xl) var(--spacing-lg);
        margin-bottom: var(--spacing-xl);
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        position: relative;
        overflow: hidden;
        border-radius: var(--spacing-sm);
    }
    
    .menu-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin: var(--spacing-md) 0;
        letter-spacing: -0.02em;
    }
    
    /* Cards avec accessibilité améliorée */
    .card {
        background-color: white;
        padding: var(--spacing-xl);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        margin-bottom: var(--spacing-xl);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: transform var(--transition-normal) ease,
                    box-shadow var(--transition-normal) ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    }
    
    .card:focus-within {
        box-shadow: 0 0 0 3px rgba(0, 160, 223, 0.4);
    }
    
    /* Feature cards avec accessibilité */
    .feature-card {
        background-color: white;
        padding: var(--spacing-xl);
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: var(--spacing-lg);
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-normal) ease;
    }
    
    .feature-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, var(--secondary-color), var(--accent-color));
        border-radius: 4px 0 0 4px;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }
    
    .feature-card:focus-within {
        box-shadow: 0 0 0 3px rgba(0, 160, 223, 0.4);
    }
    
    /* Boutons accessibles */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        padding: 0.875rem 1.5rem;
        font-weight: 500;
        border-radius: 8px;
        transition: all var(--transition-normal) ease;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 75, 135, 0.15);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    .stButton>button:focus {
        box-shadow: 0 0 0 3px rgba(0, 160, 223, 0.4);
    }
    
    /* Messages d'état accessibles */
    .message {
        padding: var(--spacing-md) var(--spacing-lg);
        border-radius: 8px;
        margin: var(--spacing-md) 0;
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
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
    
    .message-info {
        background-color: rgba(0, 160, 223, 0.1);
        color: var(--secondary-color);
        border: 1px solid rgba(0, 160, 223, 0.2);
    }
    
    /* Skip to content pour accessibilité */
    .skip-to-content {
        position: absolute;
        top: -40px;
        left: 0;
        background: var(--primary-color);
        color: white;
        padding: var(--spacing-md);
        z-index: 100;
        transition: top var(--transition-fast) ease;
    }
    
    .skip-to-content:focus {
        top: 0;
    }
    
    /* Tooltips accessibles */
    [data-tooltip] {
        position: relative;
    }
    
    [data-tooltip]:before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: var(--spacing-sm) var(--spacing-md);
        background: var(--text-color);
        color: white;
        border-radius: 4px;
        font-size: 0.875rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all var(--transition-fast) ease;
    }
    
    [data-tooltip]:hover:before,
    [data-tooltip]:focus:before {
        opacity: 1;
        visibility: visible;
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

# Création/vérification de la base de données au démarrage
engine = create_database(force_recreate=False)

# Initialisation des variables de session
if "user" not in st.session_state:
    st.session_state.user = None
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

# Sidebar avec menu élégant et accessible
with st.sidebar:
    st.markdown('<div class="menu-header" role="banner">', unsafe_allow_html=True)
    st.image(
        "https://img.icons8.com/fluency/96/000000/shield.png",
        width=80,
        output_format="PNG",
        use_column_width=False,
        caption="Logo InsureCost Analytics",
    )
    st.markdown(
        '<p class="menu-title" role="heading" aria-level="1">InsureCost Analytics</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Section utilisateur
    if st.session_state.is_authenticated:
        st.markdown(
            f'<div class="message message-success" role="status">👤 {st.session_state.user["username"]}</div>',
            unsafe_allow_html=True,
        )

    # Navigation principale
    st.markdown(
        '<nav role="navigation" aria-label="Menu principal">', unsafe_allow_html=True
    )

    # Section de connexion
    st.markdown('<div class="login-section">', unsafe_allow_html=True)
    if not st.session_state.is_authenticated:
        with st.expander("🔐 Connexion", expanded=True):
            with st.form("login_form"):
                username = st.text_input("Identifiant", key="username")
                password = st.text_input(
                    "Mot de passe", type="password", key="password"
                )
                submit = st.form_submit_button("Se connecter")

                if submit:
                    user = verify_user(engine, username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.is_authenticated = True
                        st.markdown(
                            '<div class="message message-success">✓ Connexion réussie</div>',
                            unsafe_allow_html=True,
                        )
                        st.rerun()
                    else:
                        st.markdown(
                            '<div class="message message-error">❌ Identifiants incorrects</div>',
                            unsafe_allow_html=True,
                        )
    else:
        if st.button("📤 Déconnexion"):
            st.session_state.user = None
            st.session_state.is_authenticated = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</nav>", unsafe_allow_html=True)

# Contenu principal
st.markdown('<main id="main-content" role="main">', unsafe_allow_html=True)

if not st.session_state.is_authenticated:
    # Hero section pour les utilisateurs non connectés
    st.markdown(
        """
        <div class="hero" role="banner">
            <h1 class="hero-title">🛡️ InsureCost Analytics</h1>
            <p class="hero-subtitle">
                Solution professionnelle d'analyse et de prédiction des coûts d'assurance santé
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Présentation des fonctionnalités
    st.markdown(
        '<section class="features" role="region" aria-label="Fonctionnalités">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Fonctionnalités")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône analyse">📊</div>
                <div class="feature-title">Analyse Approfondie</div>
                <p>Analysez les tendances et patterns des coûts d'assurance santé avec des visualisations avancées.</p>
            </div>
            
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône statistiques">📈</div>
                <div class="feature-title">Statistiques Détaillées</div>
                <p>Accédez à des métriques précises et des analyses statistiques sur les facteurs de coûts.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône prédiction">🎯</div>
                <div class="feature-title">Prédiction des Coûts</div>
                <p>Estimez les coûts d'assurance avec précision grâce à nos modèles prédictifs avancés.</p>
            </div>
            
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône insights">💡</div>
                <div class="feature-title">Insights Stratégiques</div>
                <p>Obtenez des recommandations basées sur les données pour optimiser la tarification.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</section>", unsafe_allow_html=True)

    # Guide de démarrage
    st.markdown(
        '<section class="guide" role="region" aria-label="Guide de démarrage">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Guide de Démarrage")
    st.markdown(
        """
        <ol role="list" style="margin-left: 1.5rem;">
            <li>Connectez-vous avec vos identifiants</li>
            <li>Accédez à l'analyse approfondie des données</li>
            <li>Utilisez l'outil de prédiction des coûts</li>
            <li>Exploitez les insights pour optimiser vos décisions</li>
        </ol>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</section>", unsafe_allow_html=True)

else:
    # Page d'accueil pour les utilisateurs connectés
    st.markdown(
        f"""
        <div class="hero" role="banner">
            <h1 class="hero-title">Bienvenue, {st.session_state.user["username"]}</h1>
            <p class="hero-subtitle">
                Accédez à vos outils d'analyse et de prédiction
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Quick links
    st.markdown(
        '<section class="quick-links" role="region" aria-label="Accès rapide">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Accès Rapide")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône analyse">📊</div>
                <div class="feature-title">Analyse Approfondie</div>
                <p>Explorez les tendances et patterns des coûts d'assurance.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("📊 Accéder à l'Analyse", key="btn_analysis"):
            st.switch_page("pages/analyse_descriptive.py")

    with col2:
        st.markdown(
            """
            <div class="feature-card" role="article">
                <div class="feature-icon" role="img" aria-label="Icône prédiction">🎯</div>
                <div class="feature-title">Prédiction des Coûts</div>
                <p>Estimez les coûts d'assurance avec précision.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("🎯 Faire une Prédiction", key="btn_prediction"):
            st.switch_page("pages/prediction_couts.py")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</section>", unsafe_allow_html=True)

    # Tableau de bord
    st.markdown(
        '<section class="dashboard" role="region" aria-label="Tableau de bord">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Tableau de Bord")
    st.markdown(
        """
        <div class="message message-info" role="status">
            ℹ️ Sélectionnez 'Analyse Approfondie' ou 'Prédiction des Coûts' dans le menu pour accéder aux fonctionnalités complètes.
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</section>", unsafe_allow_html=True)

st.markdown("</main>", unsafe_allow_html=True)

# Footer accessible
st.markdown(
    """
    <footer role="contentinfo" style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid var(--neutral-color); text-align: center;">
        <p style="color: var(--text-light);">
            © 2024 InsureCost Analytics - Tous droits réservés
        </p>
        <div style="margin-top: 1rem;">
            <a href="#" style="color: var(--secondary-color); text-decoration: none; margin: 0 1rem;">Politique de confidentialité</a>
            <a href="#" style="color: var(--secondary-color); text-decoration: none; margin: 0 1rem;">Conditions d'utilisation</a>
            <a href="#" style="color: var(--secondary-color); text-decoration: none; margin: 0 1rem;">Contact</a>
        </div>
    </footer>
""",
    unsafe_allow_html=True,
)
