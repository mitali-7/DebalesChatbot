import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://debales.ai"
visited = set()

def get_all_links(url):
    links = set()
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(BASE_URL, href)

            # only internal links
            if BASE_URL in full_url:
                links.add(full_url)

    except:
        pass

    return links


def scrape_page(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # remove noise
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)

    except:
        return ""


def crawl(start_url):
    to_visit = [start_url]
    all_text = ""

    while to_visit:
        url = to_visit.pop()

        if url in visited:
            continue

        print(f"Scraping: {url}")
        visited.add(url)

        text = scrape_page(url)
        all_text += text + "\n\n"

        links = get_all_links(url)

        for link in links:
            if link not in visited:
                to_visit.append(link)

    return all_text


if __name__ == "__main__":
    data = crawl(BASE_URL)

    with open("data.txt", "w", encoding="utf-8") as f:
        f.write(data)

    print("✅ Full site scraping complete")