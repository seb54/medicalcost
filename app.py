import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import seaborn as sns
import matplotlib.pyplot as plt
from models.cost_predictor import CostPredictor
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Coûts Médicaux",
    page_icon="🏥",
    layout="wide"
)

# Fonction pour charger les données
@st.cache_data
def load_data():
    engine = create_engine('sqlite:///data/medical_costs.db')
    query = """
    SELECT 
        p.age,
        p.nb_children,
        p.bmi,
        p.insurance_cost,
        s.sex_type as sex,
        sm.smoking_status as smoker,
        r.region_name as region
    FROM PATIENT p
    JOIN SEX s ON p.id_sex = s.id_sex
    JOIN SMOKING sm ON p.id_smoking_status = sm.id_smoking_status
    JOIN REGION r ON p.id_region = r.id_region
    """
    return pd.read_sql(query, engine)

# Chargement du modèle en cache
@st.cache_resource
def load_model():
    predictor = CostPredictor()
    return predictor

# Chargement des données
df = load_data()
# Chargement du modèle
model = load_model()

# Sidebar pour la navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Analyse Descriptive", "Prédiction des Coûts"])

if page == "Analyse Descriptive":
    # Titre de l'application
    st.title("📊 Analyse des Coûts Médicaux")

    # Affichage des statistiques générales
    st.header("📈 Statistiques Générales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Coût Moyen", f"${df['insurance_cost'].mean():,.2f}")
    with col2:
        st.metric("Coût Médian", f"${df['insurance_cost'].median():,.2f}")
    with col3:
        st.metric("Coût Maximum", f"${df['insurance_cost'].max():,.2f}")
    with col4:
        st.metric("Coût Minimum", f"${df['insurance_cost'].min():,.2f}")

    # Distribution des coûts
    st.header("📊 Distribution des Coûts d'Assurance")
    fig = px.histogram(df, x="insurance_cost", nbins=50,
                      title="Distribution des Coûts d'Assurance",
                      labels={"insurance_cost": "Coût d'Assurance ($)",
                             "count": "Nombre de Patients"})
    st.plotly_chart(fig)

    # Analyse par facteur
    st.header("🔍 Analyse par Facteur")

    # Sélection du facteur à analyser
    factor = st.selectbox(
        "Choisissez un facteur à analyser",
        ["age", "bmi", "nb_children", "sex", "smoker", "region"]
    )

    col1, col2 = st.columns(2)

    with col1:
        # Box plot
        fig1 = px.box(df, x=factor, y="insurance_cost",
                      title=f"Distribution des Coûts par {factor}",
                      labels={"insurance_cost": "Coût d'Assurance ($)"})
        st.plotly_chart(fig1)

    with col2:
        # Violin plot
        fig2 = px.violin(df, x=factor, y="insurance_cost",
                         title=f"Distribution Détaillée des Coûts par {factor}",
                         labels={"insurance_cost": "Coût d'Assurance ($)"})
        st.plotly_chart(fig2)

    # Analyse multivariée
    st.header("🔄 Analyse Multivariée")

    # Création d'un DataFrame pour l'analyse des variables catégorielles
    df_encoded = df.copy()
    # Encodage des variables catégorielles
    df_encoded['smoker_encoded'] = (df_encoded['smoker'] == 'yes').astype(int)
    df_encoded['sex_encoded'] = (df_encoded['sex'] == 'male').astype(int)
    
    # Création de variables dummy pour la région
    region_dummies = pd.get_dummies(df_encoded['region'], prefix='region')
    df_encoded = pd.concat([df_encoded, region_dummies], axis=1)

    # Sélection des colonnes pour la matrice de corrélation
    correlation_columns = ['age', 'bmi', 'nb_children', 'insurance_cost', 
                         'smoker_encoded', 'sex_encoded'] + list(region_dummies.columns)
    
    # Calcul de la matrice de corrélation
    corr_matrix = df_encoded[correlation_columns].corr()

    # Affichage de la matrice de corrélation
    st.subheader("Matrice de Corrélation Complète")
    
    # Renommage des colonnes pour plus de clarté
    column_names = {
        'age': 'Âge',
        'bmi': 'IMC',
        'nb_children': 'Nb Enfants',
        'insurance_cost': 'Coût Assurance',
        'smoker_encoded': 'Fumeur',
        'sex_encoded': 'Sexe (H)',
        'region_southwest': 'Sud-Ouest',
        'region_southeast': 'Sud-Est',
        'region_northwest': 'Nord-Ouest',
        'region_northeast': 'Nord-Est'
    }
    
    corr_matrix_renamed = corr_matrix.rename(columns=column_names, index=column_names)
    
    fig = px.imshow(corr_matrix_renamed,
                    labels=dict(color="Corrélation"),
                    color_continuous_scale="RdBu",
                    aspect="auto")
    fig.update_layout(height=800)
    st.plotly_chart(fig)

    # Analyse détaillée de l'impact du tabagisme
    st.header("🚬 Impact du Tabagisme sur les Coûts d'Assurance")
    
    # Calcul des statistiques par groupe
    smoking_stats = df.groupby('smoker')['insurance_cost'].agg(['mean', 'median', 'std']).round(2)
    smoking_stats.columns = ['Coût Moyen', 'Coût Médian', 'Écart-Type']
    
    # Affichage des statistiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Statistiques par Groupe")
        st.dataframe(smoking_stats.style.format({
            'Coût Moyen': '${:,.2f}',
            'Coût Médian': '${:,.2f}',
            'Écart-Type': '${:,.2f}'
        }))
        
        # Calcul de la différence en pourcentage
        pct_difference = ((smoking_stats.loc['yes', 'Coût Moyen'] - 
                          smoking_stats.loc['no', 'Coût Moyen']) / 
                         smoking_stats.loc['no', 'Coût Moyen'] * 100)
        
        st.info(f"💡 En moyenne, les fumeurs paient **{pct_difference:.1f}%** plus cher que les non-fumeurs.")
    
    with col2:
        # Création d'un violin plot pour comparer les distributions
        fig = px.violin(df, x="smoker", y="insurance_cost", box=True,
                       title="Distribution des Coûts par Statut Tabagique",
                       labels={"insurance_cost": "Coût d'Assurance ($)",
                              "smoker": "Statut Tabagique"},
                       color="smoker")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
    
    # Analyse croisée avec d'autres facteurs
    st.subheader("🔄 Interaction avec d'autres facteurs")
    
    # Sélection du facteur à croiser
    factor = st.selectbox(
        "Analyser l'impact du tabagisme en fonction de :",
        ["age", "bmi", "sex", "region"],
        key="smoking_analysis"
    )
    
    if factor in ["age", "bmi"]:
        # Scatter plot pour variables numériques
        fig = px.scatter(df, x=factor, y="insurance_cost", color="smoker",
                        title=f"Coûts d'Assurance par {factor} et Statut Tabagique",
                        labels={"insurance_cost": "Coût d'Assurance ($)"},
                        trendline="ols")
        st.plotly_chart(fig)
        
        # Calcul des corrélations par groupe
        correlations = df.groupby('smoker')[[factor, 'insurance_cost']].corr().reset_index()
        correlations = correlations[correlations['level_1'] == factor]['insurance_cost']
        st.write(f"Corrélation avec {factor}:")
        st.write(f"- Non-fumeurs : {correlations.iloc[0]:.2f}")
        st.write(f"- Fumeurs : {correlations.iloc[1]:.2f}")
        
    else:
        # Box plot pour variables catégorielles
        fig = px.box(df, x=factor, y="insurance_cost", color="smoker",
                     title=f"Distribution des Coûts par {factor} et Statut Tabagique",
                     labels={"insurance_cost": "Coût d'Assurance ($)"})
        st.plotly_chart(fig)
        
        # Calcul des moyennes par groupe
        means = df.groupby([factor, 'smoker'])['insurance_cost'].mean().unstack()
        st.write("Coût moyen par groupe :")
        st.dataframe(means.style.format('${:,.2f}'))
    
    # Ajout d'insights supplémentaires
    st.subheader("💡 Insights Clés")
    st.markdown("""
    - Le tabagisme est l'un des facteurs les plus importants dans la détermination des coûts d'assurance
    - L'impact du tabagisme est constant à travers différentes tranches d'âge
    - L'effet combiné du tabagisme et d'un IMC élevé peut conduire à des coûts particulièrement élevés
    - La différence de coût entre fumeurs et non-fumeurs est significative dans toutes les régions
    """)

    # Interprétation des corrélations
    st.subheader("💡 Interprétation des Corrélations")
    
    # Trouver les corrélations les plus fortes avec le coût d'assurance
    correlations_with_cost = corr_matrix['insurance_cost'].sort_values(ascending=False)
    
    st.write("**Principales corrélations avec le coût d'assurance :**")
    for var, corr in correlations_with_cost.items():
        if var != 'insurance_cost' and abs(corr) > 0.1:  # Seuil de corrélation significative
            impact = "positive" if corr > 0 else "négative"
            strength = "forte" if abs(corr) > 0.5 else "modérée" if abs(corr) > 0.3 else "faible"
            st.write(f"- {column_names.get(var, var)} : Corrélation {impact} {strength} ({corr:.2f})")

    # Scatter plot interactif
    st.subheader("Relation entre Variables")
    x_axis = st.selectbox("Choisissez la variable X", correlation_columns)
    y_axis = st.selectbox("Choisissez la variable Y", correlation_columns)
    color_var = st.selectbox("Colorer par", ["sex", "smoker", "region"])

    fig = px.scatter(df_encoded, x=x_axis, y=y_axis, color=color_var,
                     title=f"{y_axis} vs {x_axis} (coloré par {color_var})")
    st.plotly_chart(fig)

else:  # Page de prédiction
    st.title("🔮 Prédiction des Coûts d'Assurance")
    
    # Formulaire de prédiction
    st.header("Entrez les informations du patient")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Âge", min_value=18, max_value=100, value=30)
        bmi = st.number_input("IMC", min_value=10.0, max_value=50.0, value=25.0)
        nb_children = st.number_input("Nombre d'enfants", min_value=0, max_value=10, value=0)
    
    with col2:
        sex = st.selectbox("Sexe", ["male", "female"])
        smoker = st.selectbox("Fumeur", ["no", "yes"])
        region = st.selectbox("Région", ["southwest", "southeast", "northwest", "northeast"])
    
    if st.button("Prédire le coût"):
        # Préparation des données pour la prédiction
        features = {
            'age': age,
            'bmi': bmi,
            'nb_children': nb_children,
            'sex': sex,
            'smoker': smoker,
            'region': region
        }
        
        try:
            # Prédiction avec le modèle en cache
            prediction = model.predict(features)
            
            # Affichage du résultat
            st.success(f"Coût d'assurance prédit : ${prediction[0]:,.2f}")
            
            # Affichage des facteurs importants
            st.header("Facteurs influençant la prédiction")
            
            # Comparaison avec les moyennes
            comparison_data = {
                'Valeur': [age, bmi, nb_children],
                'Moyenne': [
                    df['age'].mean(),
                    df['bmi'].mean(),
                    df['nb_children'].mean()
                ]
            }
            comparison_df = pd.DataFrame(comparison_data, index=['Âge', 'IMC', 'Nombre d\'enfants'])
            
            fig = go.Figure(data=[
                go.Bar(name='Valeur actuelle', x=comparison_df.index, y=comparison_df['Valeur']),
                go.Bar(name='Moyenne', x=comparison_df.index, y=comparison_df['Moyenne'])
            ])
            fig.update_layout(barmode='group', title="Comparaison avec les moyennes de la base de données")
            st.plotly_chart(fig)
            
        except Exception as e:
            st.error(f"Erreur lors de la prédiction : {str(e)}")

# Affichage des données brutes
st.header("📋 Données Brutes")
if st.checkbox("Afficher les données brutes"):
    st.write(df) 