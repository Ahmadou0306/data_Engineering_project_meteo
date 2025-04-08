from pyspark.sql import SparkSession
from pyspark.sql.functions import col, substring, to_date, concat_ws, to_timestamp, lit
import pandas as pd
import atexit


spark = SparkSession.builder \
    .appName("Météo") \
    .config("spark.python.worker.reuse", "true") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.network.timeout", "600s") \
    .getOrCreate()


def __date_hour_colonne__(dataframe):
    # Créer le DataFrame Spark depuis Pandas
    df = spark.createDataFrame(pd.DataFrame(dataframe))
    
    # Sauvegarder la date brute dans une nouvelle colonne temporaire
    df = df.withColumn("date_str", col("date").cast("string"))
    
    # Extraire la date et l'heure
    df = df.withColumn("date_formatted", to_date(substring(col("date_str"), 1, 8), "yyyyMMdd")) \
           .withColumn("heure_formatted", concat_ws(":", substring(col("date_str"), 9, 2), lit("00"), lit("00"))) \
           #.withColumn("heure_formatted", concat_ws(" ", col("date_formatted"), col("heure_str"))) \
    
    # Obtenir une liste de colonnes sans les colonnes temporaires et les colonnes à remplacer
    all_columns = [c for c in df.columns if c not in ["date_str", "heure_str", "date", "heure", "date_formatted", "heure_formatted"]]
    
    # Sélectionner les colonnes originales plus les nouvelles colonnes transformées
    df = df.select(
        *all_columns,
        col("date_formatted").alias("date"),
        col("heure_formatted").alias("heure"),
    )
    
    return df

def __nan_value_manage__(df):
    return df.dropna()

def __duplicate_value_manage__(df):
    return df.dropDuplicates()

def __transformer_header__(df):
    # Dictionnaire de correspondance entre les anciennes colonnes et les nouvelles colonnes
    header_map = {
        'ville': 'ville',
        'pays': 'pays',
        'T2M': 'temperature_air',
        'PS': 'pression',
        'WS10M': 'intensite_vent',
        'QV2M': 'humidite_specifique',
        'T2MDEW': 'temperature_point_rosee',
        'U10M': 'composante_est_ouest_vent',
        'V10M': 'vitesse_vent',
        'RH2M': 'humidite_relative',
        'WD10M': 'direction_vent',
        'T2MWET': 'temperature_humide',
        'PRECTOTCORR': 'precipitations_corrigees',
        'date': 'date',
        'heure': 'heure'
    }
    
    # Renommer les colonnes du DataFrame
    df.rename(columns=header_map, inplace=True)
    
    return df

def cleaning_data(dataframe):
    df = __date_hour_colonne__(dataframe)
    # nan_value_manage
    df = __nan_value_manage__(df)
    # nan_value_manage
    df = __duplicate_value_manage__(df)

    #convert pandas 
    df_cleaned = df.toPandas()

    df_cleaned = __transformer_header__(df_cleaned)
    return df_cleaned


def close_spark():
    spark.stop()
    print("session spark terminé")


atexit.register(close_spark)