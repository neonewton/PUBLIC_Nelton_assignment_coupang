from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import random


# ----- Setup -----
chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
base_url = "https://www.zalora.sg/c/men/shoes/c-27?page="
output_file = "zalora_shoes_full_output.csv"

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

print("✅ Chrome WebDriver attached")

items = []
max_pages = 3  # set how many pages you want to scrape

for page_num in range(1, max_pages + 1):
    url = f"{base_url}{page_num}"
    print(f"🌐 Scraping Page {page_num}: {url}")
    driver.get(url)

    try:
        time.sleep(random.uniform(10, 9))
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test-id="productTitle"]'))
        )
    except Exception as e:
        print(f"⚠️ Timeout on page {page_num}: {e}")
        continue

    soup = BeautifulSoup(driver.page_source, "html.parser")
    if soup.select_one(".px-captcha-container"):
        print(f"🚫 CAPTCHA triggered on page {page_num}. Skipping...")
        continue
    title_tags = soup.select('[data-test-id="productTitle"]')
    price_tags = soup.select('span.font-bold.text-base')
    image_tags = soup.select('img[alt]')
    link_tags = soup.select('a[href^="/"]')  # relative product links

    # Filter only product card links (avoid navigation/header links)
    product_links = [a["href"] for a in link_tags if "/p/" in a["href"]]
    product_links = list(dict.fromkeys(product_links))  # remove duplicates

    for i in range(min(len(title_tags), len(price_tags), len(image_tags), len(product_links))):
        title = title_tags[i].text.strip()
        price = price_tags[i].text.strip().replace("S$", "SGD")
        image_url = image_tags[i].get("src")
        product_url = "https://www.zalora.sg" + product_links[i]
        items.append([title, price, image_url, product_url])

    time.sleep(2)  # be nice to the server

# ----- Output to CSV -----
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Price", "ImageURL", "ProductURL"])
    writer.writerows(items)

print(f"✅ Done. Scraped {len(items)} products across {max_pages} pages.")
print(f"📄 CSV saved to: {output_file}")




# 1245 pm 19 Jul
"""
🔍 Why It Happened
Common causes include:

Scraping too quickly (e.g., no delays, fast page loops)

Default browser automation fingerprints (e.g., Selenium with no anti-detection settings)

Repeated requests from same IP (Zalora is aggressive about rate limiting)

"""