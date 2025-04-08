from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timedelta
from etl_service.extract_service import get_data
from etl_service.transform_service import cleaning_data
from etl_service.load_service import insert_postgres_data


app = Flask(__name__)

DELAY = 4 #Jours

def extract():
    date_delay = datetime.today() - timedelta(days=DELAY)
    date = date_delay.strftime("%Y%m%d")
    return get_data(["senegal","mali","cote_d_ivoire","guinee","nigeria","ghana","burkina faso"],date,date)

def transform(df):
    return cleaning_data(df)

def load_data(df):
    insert_postgres_data(df)


def task_etl():
    print("Récupération des données ...")
    df = extract()
    print("données récupéré !!!")
    print("Nettoyage des données...")
    df = transform(df)
    print("donnée Nettoyer !!!")
    load_data(df)
    print("Donnée charger !!!")
    print(f"Exécution de l'ETL à {time.strftime('%Y-%m-%d %H:%M:%S')}")

scheduler = BackgroundScheduler()
scheduler.add_job(task_etl, 'interval', hours=24)

#task_etl()
scheduler.start()

@app.route('/')
def home():
    return "Flask ETL Scheduler is running!"

if __name__ == '__main__':
    app.run(debug=True)
