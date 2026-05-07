import requests
from datetime import datetime


def get_meteo(oras: str = "Craiova") -> dict:
    try:
        url = f"https://wttr.in/{oras}?format=j1&lang=ro"
        r = requests.get(url, timeout=8)
        data = r.json()

        current = data["current_condition"][0]
        azi = data["weather"][0]
        maine = data["weather"][1]

        return {
            "success": True,
            "oras": oras,
            "temp": current["temp_C"],
            "feels_like": current["FeelsLikeC"],
            "descriere": current["lang_ro"][0]["value"] if current.get("lang_ro") else current["weatherDesc"][0]["value"],
            "umiditate": current["humidity"],
            "vant": current["windspeedKmph"],
            "max_azi": azi["maxtempC"],
            "min_azi": azi["mintempC"],
            "max_maine": maine["maxtempC"],
            "min_maine": maine["mintempC"],
        }
    except Exception as e:
        return {"success": False, "eroare": str(e)}


def get_curs_valutar(baza: str = "EUR", tinta: str = "RON") -> dict:
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{baza}"
        r = requests.get(url, timeout=8)
        data = r.json()

        curs = data["rates"].get(tinta)
        if curs is None:
            return {"success": False, "eroare": f"Valuta {tinta} negasita"}

        return {
            "success": True,
            "baza": baza,
            "tinta": tinta,
            "curs": round(curs, 4),
            "data": data.get("date", "")
        }
    except Exception as e:
        return {"success": False, "eroare": str(e)}