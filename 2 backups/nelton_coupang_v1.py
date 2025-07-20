import requests
from bs4 import BeautifulSoup
import csv

URL = "https://www.zalora.sg/c/men/shoes/c-27?page=1"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

resp = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(resp.text, "html.parser")

items = []
for product in soup.select("._95f5u4"):
    title_tag = product.select_one("._0xLoFW")
    price_tag = product.select_one("._0xLoFW+ div")
    
    title = title_tag.text.strip() if title_tag else ""
    price = price_tag.text.strip() if price_tag else ""
    
    items.append([title, price])

with open("zalora_v1_simple.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Price"])
    writer.writerows(items)

# 1220 pm 19 Jul
"""
Yes, absolutely — if the requests + BeautifulSoup method produces an empty .csv, it's likely because Zalora renders the product content dynamically via JavaScript, which BeautifulSoup cannot see in static HTML.

Using Selenium with a Chrome WebDriver attached to an existing debugging session is a good workaround — it lets you inspect the fully rendered DOM, exactly like what you see in Chrome.


"""