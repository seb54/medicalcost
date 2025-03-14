import bcrypt
from sqlalchemy import text
from loguru import logger


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(
    engine, username: str, password: str, email: str = None, is_admin: bool = False
):
    """Crée un nouvel utilisateur"""
    try:
        with engine.connect() as conn:
            # Récupération de l'ID du type d'utilisateur
            user_type = "admin" if is_admin else "user"
            result = conn.execute(
                text("SELECT id_user_type FROM USER_TYPE WHERE type_name = :type"),
                {"type": user_type},
            ).fetchone()

            if not result:
                raise ValueError(f"Type d'utilisateur {user_type} non trouvé")

            user_type_id = result[0]

            # Hash du mot de passe
            hashed_password = hash_password(password)

            # Insertion de l'utilisateur
            conn.execute(
                text(
                    """
                    INSERT INTO USER_ACCOUNT (username, email, password_hash, id_user_type)
                    VALUES (:username, :email, :password_hash, :user_type_id)
                """
                ),
                {
                    "username": username,
                    "email": email,
                    "password_hash": hashed_password,
                    "user_type_id": user_type_id,
                },
            )
            conn.commit()
            logger.info(f"Utilisateur {username} créé avec succès")

    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur : {str(e)}")
        raise


def verify_user(engine, username: str, password: str) -> dict:
    """Vérifie les identifiants d'un utilisateur et retourne ses informations"""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT ua.id_user_account, ua.password_hash, ua.email, ut.type_name
                FROM USER_ACCOUNT ua
                JOIN USER_TYPE ut ON ua.id_user_type = ut.id_user_type
                WHERE ua.username = :username
            """
            ),
            {"username": username},
        ).fetchone()

        if not result:
            return None

        user_id, stored_hash, email, user_type = result

        if verify_password(password, stored_hash):
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "is_admin": user_type == "admin",
            }

        return None
