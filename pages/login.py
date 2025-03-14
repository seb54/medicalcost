import streamlit as st
import time
from datetime import datetime
from modules.auth import verify_user
from modules.db_loader import create_database

# Styles personnalisés pour l'accessibilité
st.markdown(
    """
<style>
    /* Amélioration de l'accessibilité */
    .login-container {
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .form-field {
        margin-bottom: 1.5rem;
    }
    
    .form-field label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #2C3345;
    }
    
    .error-message {
        color: #E41E31;
        background-color: rgba(228, 30, 49, 0.1);
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .success-message {
        color: #00B67A;
        background-color: rgba(0, 182, 122, 0.1);
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    /* Support de la navigation au clavier */
    :focus {
        outline: 2px solid #00A0DF;
        outline-offset: 2px;
    }
    
    /* Amélioration du contraste */
    .stButton>button {
        background: #004B87;
        color: white;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background: #00A0DF;
    }
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialise les variables de session avec gestion de sécurité améliorée"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "last_attempt_time" not in st.session_state:
        st.session_state.last_attempt_time = None
    if "locked_until" not in st.session_state:
        st.session_state.locked_until = None


def check_rate_limiting() -> bool:
    """Vérifie les limitations de tentatives de connexion"""
    current_time = time.time()

    # Réinitialisation après 5 minutes
    if st.session_state.locked_until and current_time > st.session_state.locked_until:
        st.session_state.login_attempts = 0
        st.session_state.locked_until = None
        return True

    # Vérification du verrouillage
    if st.session_state.locked_until:
        remaining_time = int(st.session_state.locked_until - current_time)
        st.error(
            f"🔒 Compte temporairement verrouillé. Réessayez dans {remaining_time} secondes."
        )
        return False

    # Vérification des tentatives
    if st.session_state.login_attempts >= 3:
        st.session_state.locked_until = current_time + 300  # 5 minutes
        st.error("🚫 Trop de tentatives. Compte verrouillé pour 5 minutes.")
        return False

    return True


def login_user(username: str, password: str) -> bool:
    """Tente de connecter l'utilisateur avec gestion de sécurité améliorée"""
    if not check_rate_limiting():
        return False

    engine = create_database()
    user = verify_user(engine, username, password)

    if user:
        st.session_state.user = user
        st.session_state.is_authenticated = True
        st.session_state.login_attempts = 0
        st.session_state.last_login = datetime.now()
        return True

    st.session_state.login_attempts += 1
    st.session_state.last_attempt_time = time.time()
    return False


def logout_user():
    """Déconnecte l'utilisateur avec nettoyage de session"""
    for key in ["user", "is_authenticated", "last_login"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("👋 Vous avez été déconnecté avec succès!")


def show_login_page():
    """Affiche la page de login avec accessibilité améliorée"""
    st.markdown(
        """
        <div class="login-container">
            <h1 style='color: #004B87; font-size: 2rem; margin-bottom: 1.5rem;'>
                🔐 Connexion Sécurisée
            </h1>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Initialisation de la session
    init_session_state()

    # Si déjà connecté
    if st.session_state.is_authenticated:
        st.markdown(
            """
            <div class="login-container">
                <div class="success-message">
                    ✅ Connecté avec succès
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.write(f"👤 Utilisateur : {st.session_state.user['username']}")
        if "last_login" in st.session_state:
            st.write(
                f"🕒 Dernière connexion : {st.session_state.last_login.strftime('%d/%m/%Y %H:%M')}"
            )

        if st.button("📤 Déconnexion"):
            logout_user()
            st.experimental_rerun()
        return

    # Formulaire de connexion
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input(
            "Nom d'utilisateur",
            help="Entrez votre identifiant",
            placeholder="Votre identifiant",
            key="username_input",
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
            help="Minimum 8 caractères, incluant majuscules, chiffres et caractères spéciaux",
            placeholder="Votre mot de passe",
            key="password_input",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("🔑 Se connecter")
        with col2:
            st.markdown(
                "<div style='padding-top: 1rem;'><a href='#' style='color: #00A0DF;'>Mot de passe oublié ?</a></div>",
                unsafe_allow_html=True,
            )

        if submit:
            if not username or not password:
                st.error("⚠️ Veuillez remplir tous les champs")
            elif login_user(username, password):
                st.success("✅ Connexion réussie!")
                st.experimental_rerun()
            else:
                st.error("❌ Identifiants incorrects")

    # Informations de sécurité
    st.markdown(
        """
        <div class="login-container" style="margin-top: 2rem;">
            <h3 style="color: #004B87; font-size: 1.2rem; margin-bottom: 1rem;">
                🛡️ Conseils de Sécurité
            </h3>
            <ul style="color: #4A5568; margin-left: 1.5rem;">
                <li>Utilisez un mot de passe fort et unique</li>
                <li>Ne partagez jamais vos identifiants</li>
                <li>Déconnectez-vous après utilisation</li>
                <li>Évitez les réseaux publics non sécurisés</li>
            </ul>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    show_login_page()
