import requests
from bs4 import BeautifulSoup

URLS = [
    "https://debales.ai",
    "https://debales.ai/blog",
]

def scrape():
    all_text = ""

    for url in URLS:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")

            for p in soup.find_all("p"):
                all_text += p.get_text() + "\n"

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    with open("data.txt", "w", encoding="utf-8") as f:
        f.write(all_text)

    print("✅ Scraping complete")

if __name__ == "__main__":
    scrape()