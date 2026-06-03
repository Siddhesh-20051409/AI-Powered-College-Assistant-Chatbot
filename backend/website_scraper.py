import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mysql.connector
import time

BASE_URL = "https://ycis.ac.in/"
MAX_PAGES = 200

DB_CONFIG = {
    "host": "localhost",
    "user": "",
    "password": "_",
    "database": "ycis_chatbot"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def clean_text(text):
    return " ".join(text.split())


def is_valid_url(url):
    parsed = urlparse(url)

    if "ycis.ac.in" not in parsed.netloc:
        return False

    blocked = (
        ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
        ".css", ".js", ".zip", ".rar", ".mp4", ".mp3"
    )

    if url.lower().endswith(blocked):
        return False

    return True


def clear_old_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM website_data")
    conn.commit()
    cursor.close()
    conn.close()
    print("Old website data deleted.")


def save_to_mysql(url, title, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO website_data (page_url, title, content)
        VALUES (%s, %s, %s)
        """,
        (url, title[:255], content)
    )

    conn.commit()
    cursor.close()
    conn.close()


def get_page_title(soup, url):
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    h2 = soup.find("h2")
    if h2 and h2.get_text(strip=True):
        return h2.get_text(strip=True)

    path = urlparse(url).path.strip("/")
    if path:
        return path.replace("-", " ").replace("/", " > ").title()

    if soup.title:
        return soup.title.get_text(strip=True)

    return "YCIS Page"


def scrape_page(url):
    print("Scraping:", url)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.encoding = "utf-8"

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type:
        print("Skipped non-html:", url)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = get_page_title(soup, url)
    content = clean_text(soup.get_text(separator=" "))

    if len(content) > 150:
        save_to_mysql(url, title, content)
        print("Saved:", title)

    links = []

    for a in soup.find_all("a", href=True):
        full_url = urljoin(url, a["href"])
        full_url = full_url.split("#")[0].strip()

        if is_valid_url(full_url):
            links.append(full_url)

    return links


def run_deep_rpa_scraper():
    clear_old_data()

    visited = set()
    to_visit = [BASE_URL]

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            new_links = scrape_page(url)
            visited.add(url)

            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

            time.sleep(1)

        except Exception as e:
            print("Error scraping:", url)
            print(e)

    print("Deep RPA scraping completed.")
    print("Total pages scraped:", len(visited))


if __name__ == "__main__":
    run_deep_rpa_scraper()