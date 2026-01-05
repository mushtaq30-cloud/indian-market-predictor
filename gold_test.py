import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.goldprice.org",
    "Referer": "https://www.goldprice.org/"
}

URL = "https://data-asg.goldprice.org/dbXRates/INR"

def fetch_gold_per_gram_inr():
    res = requests.get(URL, headers=HEADERS, timeout=10)
    res.raise_for_status()

    data = res.json()
    item = data["items"][0]

    # Gold price per ounce in INR
    ounce_price = item["xauPrice"]

    gram_price = ounce_price / 31.1035
    return round(gram_price, 2)


def fetch_silver_per_kg_inr():
    res = requests.get(URL, headers=HEADERS, timeout=10)
    res.raise_for_status()

    data = res.json()
    item = data["items"][0]

    # Silver price per ounce in INR
    ounce_price = item["xagPrice"]

    gram_price = ounce_price / 31.1035
    kg_price = gram_price * 1000

    return round(kg_price, 2)


if __name__ == "__main__":
    print("Gold 24K per gram (INR):", fetch_gold_per_gram_inr())
    print("Silver per KG (INR):", fetch_silver_per_kg_inr())
# -------- GOODRETURNS SCRAPER --------
import cloudscraper