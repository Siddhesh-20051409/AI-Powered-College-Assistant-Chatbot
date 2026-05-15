import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])

    return text

if __name__ == "__main__":
    url = "https://ycis.ac.in"   # change if needed
    data = scrape_website(url)

    with open("../data/website.txt", "w", encoding="utf-8") as f:
        f.write(data)

    print("Website data saved!")