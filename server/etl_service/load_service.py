import psycopg2
import pandas as pd

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "passer"
POSTGRES_HOST = "localhost"
DB_NAME = "meteo_db"
TABLE_NAME = "meteo_data"

def __create_postgrest_database_if_not_exist__():
    try:
        # Connexion à la base de données 'postgres' pour vérifier si 'meteo_db' existe
        conn = psycopg2.connect(dbname="postgres", user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST)
        conn.autocommit = True
        cur = conn.cursor()

        # Vérification si la base de données 'meteo_db' existe
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
        exists = cur.fetchone()
        if not exists:
            # Si la base de données n'existe pas, on la crée
            print(f"Creating database '{DB_NAME}'...")
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    

def __create_cube_if_not_exist__():
    db_name = "meteo_cube"
    try:
        # Connexion à la base 'postgres' pour vérifier si la base cible existe
        conn = psycopg2.connect(
            dbname="postgres",
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST
        )
        conn.autocommit = True  # ✅ Placer immédiatement après la connexion
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            exists = cur.fetchone()

            if not exists:
                print(f"Creating database '{db_name}'...")
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"Database '{db_name}' created successfully")
            else:
                print(f"Database '{db_name}' already exists")
        conn.close()

        # Connexion à la base de données cible pour créer les tables
        with psycopg2.connect(
            dbname=db_name,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST
        ) as conn:
            with conn.cursor() as cur:
                #cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db_name};")

                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS dim_temps (
                        id SERIAL PRIMARY KEY,
                        date_key INTEGER NOT NULL,
                        heure TIME,
                        annee INT,
                        mois INT,
                        nom_mois VARCHAR(15),
                        jours INT,
                        jours_semaine INT,
                        nom_jours VARCHAR (255)
                    );
                """)
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS dim_temperature_humide (
                        id SERIAL PRIMARY KEY,
                        temperature_humide FLOAT
                    );
                """)
                
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS dim_location (
                        id SERIAL PRIMARY KEY,
                        pays VARCHAR(255),
                        ville VARCHAR(255)
                    );
                """)
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS meteo_fait (
                    temps_id INT REFERENCES dim_temps(id),
                    temperature_humide_id INT REFERENCES dim_temperature_humide(id),
                    location_id INT REFERENCES dim_location(id),
                    humidite_relative FLOAT,
                    temperature_air FLOAT
                );
                """)
                conn.commit()
                print("Tables created successfully in database 'meteo_cube'")

    except Exception as e:
        print(f"Error creating database or tables: {e}")
        return False


def __clear_cube__():
    db_name = "meteo_cube"
    try:
        # Connexion à la base de données cible
        with psycopg2.connect(
            dbname=db_name,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST
        ) as conn:
            with conn.cursor() as cur:
                # Liste des tables à vider
                tables_to_clear = [
                    "dim_temperature_humide",
                    "dim_temps",
                    "dim_location",
                    "meteo_fait"
                ]
                
                # Exécuter TRUNCATE sur chaque table
                for table in tables_to_clear:
                    cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                    print(f"Table '{table}' cleared successfully.")
                
                # Commit des modifications
                conn.commit()

    except Exception as e:
        print(f"Error clearing tables: {e}")
        return False


# Créer la base de données et la table si elles n'existent pas
__create_postgrest_database_if_not_exist__()
__create_cube_if_not_exist__()
__clear_cube__()

def insert_postgres_data(dataframe, batch_size=200):
    __create_cube_if_not_exist__()
    __clear_cube__()
     # Connexion à PostgreSQL
    conn = psycopg2.connect(dbname=DB_NAME, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST)
    cur = conn.cursor()
    
    # Créer la table si elle n'existe pas (en respectant le bon ordre)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            ville VARCHAR(255),
            pays VARCHAR(255),
            temperature_air FLOAT,
            pression FLOAT,
            intensite_vent FLOAT,
            humidite_specifique FLOAT,
            temperature_point_rosee FLOAT,
            composante_est_ouest_vent FLOAT,
            vitesse_vent FLOAT,
            humidite_relative FLOAT,
            direction_vent FLOAT,
            temperature_humide FLOAT,
            precipitations_corrigees FLOAT,
            date DATE,
            heure VARCHAR(255)
        );
    """)
    conn.commit()
    
    # Vérifier le nombre de colonnes dans le DataFrame
    column_count = len(dataframe.columns)
    print(f"DataFrame has {column_count} columns")
    print(f"DataFrame columns: {dataframe.columns.tolist()}")
    
    # Liste des colonnes attendues dans le bon ordre
    expected_columns = [
        'ville', 'pays', 'temperature_air', 'pression', 'intensite_vent', 
        'humidite_specifique', 'temperature_point_rosee', 'composante_est_ouest_vent',
        'vitesse_vent', 'humidite_relative', 'direction_vent', 
        'temperature_humide', 'precipitations_corrigees', 'date', 'heure'
    ]
    
    # Ajuster le DataFrame
    dataframe = dataframe[expected_columns]
        
    # Préparer les données pour l'insertion
    batch = []
    for _, row in dataframe.iterrows():
        row_tuple = tuple(row.values)
        if len(row_tuple) != 15:
            print(f"Warning: Row has {len(row_tuple)} values, expected 15")
            continue
        batch.append(row_tuple)
        
        if len(batch) >= batch_size:
            try:
                query = f"""
                    INSERT INTO {TABLE_NAME} 
                    (
                        ville, pays, temperature_air, pression, intensite_vent, 
                        humidite_specifique, temperature_point_rosee, composante_est_ouest_vent,
                        vitesse_vent, humidite_relative, direction_vent, 
                        temperature_humide, precipitations_corrigees, date, heure
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.executemany(query, batch)
                conn.commit()
                print(f"Inserted batch of {len(batch)} rows")
                batch = []
            except Exception as e:
                print(f"Error inserting batch: {e}")
                if batch:
                    print(f"First row in batch: {batch[0]}")
                conn.rollback()
    
    # Insérer le dernier batch
    if batch:
        try:
            query = f"""
                INSERT INTO {TABLE_NAME} 
                (
                    ville, pays, temperature_air, pression, intensite_vent, 
                    humidite_specifique, temperature_point_rosee, composante_est_ouest_vent,
                    vitesse_vent, humidite_relative, direction_vent, 
                    temperature_humide, precipitations_corrigees, date, heure
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.executemany(query, batch)
            conn.commit()
            print(f"Inserted final batch of {len(batch)} rows")
        except Exception as e:
            print(f"Error inserting final batch: {e}")
            if batch:
                print(f"First row in batch: {batch[0]}")
            conn.rollback()
    
    print("Data insertion completed")
    cur.close()
    conn.close()
