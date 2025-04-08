import concurrent.futures
import requests
import pandas as pd


pays_coordinee = {
    "senegal": {
        "dakar": (14.6928, -17.4467),
        "thies": (14.7894, -16.926),
        "saint-louis": (16.0333, -16.5),
        "kaolack": (14.151, -16.0726),
        "ziguinchor": (12.5833, -16.2667),
        "tambacounda": (13.77, -13.6672),
        "kedougou": (12.5535, -12.1743),
    },
    "mali": {
        "bamako": (12.6392, -8.0029),
        "segou": (13.4317, -6.2157),
        "timbuktu": (16.7666, -3.0026),
        "mopti": (14.4843, -4.1827),
    },
    "cote_d_ivoire": {
        "abidjan": (5.3364, -4.0261),
        "bouake": (7.6833, -5.0333),
        "yamoussoukro": (6.8161, -5.2742),
        "san_pedro": (4.7485, -6.6363),
    },
    "guinee": {
        "conakry": (9.6412, -13.5784),
        "kankan": (10.3842, -9.3057),
        "n_zerekore": (7.7594, -8.8174),
        "labé": (11.3167, -12.2833),
    },
    "nigeria": {
        "lagos": (6.5244, 3.3792),
        "abuja": (9.0579, 7.4951),
        "kano": (12.0022, 8.5919),
    },
    "ghana": {
        "accra": (5.6037, -0.187),
        "kumasi": (6.6666, -1.6163),
        "tamale": (9.4075, -0.8531),
        "takoradi": (4.8975, -1.7603),
    },
    "burkina faso": {
        "ouagadougou": (12.3714, -1.5197),
        "bobo dioulasso": (11.1786, -4.2979),
        "koudougou": (12.2542, -2.3625),
    },
}

def __get_url__(lat:str, long:str, start_date:str, end_date:str)->str:
    return f"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=T2M,RH2M,T2MWET,PRECTOT,WS10M,WD10M,T2MDEW,V10M,PS,QV2M,U10M&community=AG&longitude={long}&latitude={lat}&start={start_date}&end={end_date}&format=json"


def __convert_to_df_optimized__(parameters, city, county):
    # Créer directement un dictionnaire avec toutes les dates
    dates = list(parameters['T2M'].keys())
    n_dates = len(dates)
    
    data = {
        'date': dates,
        'ville': [city] * n_dates,
        'pays': [county] * n_dates
    }
    
    # Ajouter les paramètres en une seule étape
    for param in parameters:
        data[param] = [parameters[param].get(date, None) for date in dates]
    
    return pd.DataFrame(data)


def get_data(pays_list, start_date, end_date):
    dfs = []
    
    def fetch_city_data(pays, ville, coordonate):
        lat, long = coordonate
        url = __get_url__(lat=lat, long=long, start_date=start_date, end_date=end_date)
        try:
            response = requests.get(url)
            data = response.json()["properties"]["parameter"]
            return __convert_to_df_optimized__(parameters=data, city=ville, county=pays)
        except Exception as e:
            print(f"Erreur pour {ville}, {pays}: {e}")
            return None
    
    tasks = []
    for pays_loop in pays_list:
        if pays_loop.lower() not in [p.lower() for p in pays_coordinee.keys()]:
            print(f"Ce pays n'est pas pris en compte: {pays_loop}")
            continue
        
        villes = pays_coordinee[pays_loop.lower()]
        for ville, coordonate in villes.items():
            tasks.append((pays_loop, ville, coordonate))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_city_data, pays, ville, coord) for pays, ville, coord in tasks]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                dfs.append(result)
    
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()



