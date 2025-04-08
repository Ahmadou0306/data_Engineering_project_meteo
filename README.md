# Projet ETL - Analyse Météorologique

## Description du projet

Ce projet consiste à collecter, transformer, et analyser des données météorologiques en utilisant un pipeline ETL (Extract, Transform, Load). Les données sont récupérées via l'API de NASA Power, nettoyées et transformées à l'aide de **Apache Spark** pour ensuite être stockées dans un **cube de données** dans une base de données **PostgreSQL**. Le projet comprend également des étapes d'analyse statistique et de modélisation avec **Machine Learning**, et la visualisation des données dans **Power BI**.

## Technologies utilisées

- **API NASA Power** : Pour la collecte des données météorologiques.
- **Apache Spark** : Pour le traitement et la transformation des données.
- **PostgreSQL** : Pour la gestion de la base de données et le stockage des données.
- **Talend** : Pour l'orchestration des jobs ETL.
- **Power BI** : Pour la visualisation des données.
- **Python** : Pour le traitement des données, la gestion du pipeline ETL et la connexion avec PostgreSQL.

## Structure du projet

Le projet est divisé en plusieurs étapes clés :

1. **Collecte des données** :
    - Les données météorologiques sont collectées via l'API de **NASA Power** à l'aide de Python, en utilisant des coordonnées géographiques spécifiques à divers pays et villes.
   
2. **Transformation et nettoyage des données** :
    - Utilisation de **Apache Spark** pour transformer et nettoyer les données :
      - Conversion des dates en colonnes distinctes pour la date et l'heure.
      - Suppression des valeurs nulles et des doublons.
      - Renommage des colonnes pour plus de clarté.

3. **Création du cube de données** :
    - Mise en place d'un schéma en étoile dans **PostgreSQL** avec des tables de dimensions (temps, température et humidité, localisation) et une table des faits.

4. **Chargement des données dans PostgreSQL** :
    - Insertion des données nettoyées dans **PostgreSQL** via un processus de batch pour accélérer l'insertion.

5. **Visualisation des données** :
    - Utilisation de **Power BI** pour créer des visualisations interactives des données météorologiques, en analysant les variables telles que la température de l'air, l'humidité relative, et d'autres facteurs temporels et géographiques.

6. **Analyse statistique et Machine Learning** :
    - Bien que cela dépasse le cadre traditionnel d'un processus ETL, cette étape permet une analyse avancée des données via des techniques statistiques et des modèles de **Machine Learning** pour effectuer des prévisions et classer des types de climats.

## Installation

### Prérequis

- Python 3.x
- Apache Spark
- PostgreSQL
- Talend (pour orchestrer les jobs ETL)
- Power BI (pour la visualisation)

### Installation des dépendances

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/username/repository-name.git
   cd repository-name
   ```

2. Installez les dépendances Python :

   ```bash
   pip install -r requirements.txt
   ```

### Configuration de PostgreSQL

1. Créez une base de données PostgreSQL, nommée `meteo_cube`, en utilisant la fonction Python suivante ou via une interface PostgreSQL.

2. Créez les tables de dimensions et la table des faits dans la base de données.

### Connexion avec Talend

1. Connectez votre base de données **meteo_db** et votre cube **meteo_cube** à **Talend**.
2. Exécutez le job Talend pour remplir les tables de dimensions.

## Utilisation

### Collecte des données

La collecte des données s'effectue via l'API de **NASA Power** avec la fonction suivante dans **Python** :

```python
def get_data(lat, long, start_date, end_date):
    # Code pour récupérer les données de l'API NASA Power
    pass
```

### Transformation des données

Le nettoyage et la transformation des données sont effectués avec **Apache Spark** :

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('MeteoData').getOrCreate()

# Chargement et transformation des données
df = spark.read.json('path_to_data')
# Transformation et nettoyage
df_cleaned = df.dropna().dropDuplicates()
df_cleaned.show()
```

### Insertion des données dans PostgreSQL

Les données nettoyées sont ensuite insérées dans PostgreSQL via le code Python ci-dessous :

```python
import psycopg2

def insert_data_into_postgres():
    # Connexion à la base de données
    conn = psycopg2.connect(dbname='meteo_cube', user='username', password='password', host='localhost')
    cursor = conn.cursor()

    # Insertion des données dans les tables
    cursor.execute('''INSERT INTO meteo_fait (temps_id, temperature_humide_id, location_id, humidite_relative, temperature_air) VALUES (%s, %s, %s, %s, %s)''', data)
    conn.commit()

    cursor.close()
    conn.close()
```

## Visualisation avec Power BI

Les données peuvent être visualisées dans **Power BI** via des graphiques interactifs. Les variables analysées incluent :

- Température de l'air (`temperature_air`)
- Humidité relative (`humidite_relative`)
- Temps (`date`, `heure`, `mois`, `année`, etc.)
- Température humide (`temperature_humide`)
- Localisation (pays, ville)

## Conclusion

Ce projet met en œuvre un processus ETL complet de collecte, transformation, et stockage des données météorologiques, tout en intégrant une analyse avancée via des outils de **Machine Learning** et de **visualisation**. Il offre un pipeline efficace et automatisé pour analyser des données complexes et en tirer des insights pertinents.

## Auteurs

- **Nom** : Ahmadou NDIAYE  
- **Email** : ahmadou.ndiaye030602@gmail.com


