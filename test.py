import time
import cloudscraper
import requests
from bs4 import BeautifulSoup


scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False
    }
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}


def clean(v: str):
    return v.replace("₹", "").replace(",", "").strip()


# -------- GOODRETURNS GOLD --------
def get_goodreturns_gold():
    url = "https://www.goodreturns.in/gold-rates/hyderabad.html"
    r = scraper.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    prices = {}
    table = soup.find("table")
    if not table:
        return prices

    for row in table.find_all("tr"):
        cols = [c.text.strip() for c in row.find_all("td")]
        if len(cols) != 2:
            continue

        text = cols[0].lower()

        if "24" in text:
            prices["Gold_24K_1g"] = clean(cols[1])
        elif "22" in text:
            prices["Gold_22K_1g"] = clean(cols[1])

    return prices


# -------- GOODRETURNS SILVER --------
def get_goodreturns_silver():
    url = "https://www.goodreturns.in/silver-rates/hyderabad.html"
    r = scraper.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        return {}

    for row in table.find_all("tr"):
        cols = [c.text.strip() for c in row.find_all("td")]
        if len(cols) == 2 and "1 Kg" in cols[0]:
            return {"Silver_1kg": clean(cols[1])}

    return {}


# -------- MCX LIVE --------
def get_mcx_prices():
    url = "https://bullions.co.in/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    gold = soup.select_one("td:-soup-contains('Gold - India MCX') + td")
    silver = soup.select_one("td:-soup-contains('Silver - India MCX') + td")

    if not gold or not silver:
        return {}

    return {
        "Gold_MCX_10g": clean(gold.text),
        "Silver_MCX_1kg_MCX": clean(silver.text)
    }


# -------- DISPLAY LOOP --------
if __name__ == "__main__":
    while True:
        final = {}

        try:
            final.update(get_goodreturns_gold())
        except Exception as e:
            print("Gold fetch failed:", e)

        try:
            final.update(get_goodreturns_silver())
        except Exception as e:
            print("Silver fetch failed:", e)

        try:
            final.update(get_mcx_prices())
        except Exception as e:
            print("MCX fetch failed:", e)

        print("\n================ LIVE HYDERABAD RATES ================")
        for k, v in final.items():
            print(f"{k} : ₹{v}")
        print("======================================================\n")

        time.sleep(15)   # refresh interval
