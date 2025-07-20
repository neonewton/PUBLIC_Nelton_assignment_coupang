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

# ---------- Configuration ----------
chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
base_url = "https://www.zalora.sg/c/men/shoes/c-27?page="
output_file = "zalora_shoes_full_output.csv"
max_pages = 3  # Number of pages to scrape
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# ---------- Setup WebDriver ----------
options = Options()
options.add_argument(f"user-agent={user_agent}")
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

print("✅ Chrome WebDriver attached")

# ---------- Scraping Loop ----------
items = []

for page_num in range(1, max_pages + 1):
    url = f"{base_url}{page_num}"
    print(f"\n🌐 Scraping Page {page_num}: {url}")
    driver.get(url)

    # Wait randomly to reduce bot detection risk
    time.sleep(random.uniform(10, 50))

    # Check for CAPTCHA first
    soup = BeautifulSoup(driver.page_source, "html.parser")
    if soup.select_one(".px-captcha-container"):
        print(f"🚫 CAPTCHA triggered on page {page_num}. Skipping...")
        continue

    try:
        # Wait for product titles to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test-id="productTitle"]'))
        )
    except Exception as e:
        print(f"⚠️ Timeout on page {page_num}: {e}")
        continue

    # Re-parse after waiting
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title_tags = soup.select('[data-test-id="productTitle"]')
    price_tags = soup.select('span.font-bold.text-base')
    image_tags = soup.select('img[alt]')
    link_tags = soup.select('a[href^="/"]')

    # Filter and de-duplicate product links
    product_links = [a["href"] for a in link_tags if "/p/" in a["href"]]
    product_links = list(dict.fromkeys(product_links))

    # Extract data safely
    for i in range(min(len(title_tags), len(price_tags), len(image_tags), len(product_links))):
        title = title_tags[i].text.strip()
        price = price_tags[i].text.strip().replace("S$", "SGD")
        image_url = image_tags[i].get("src")
        product_url = "https://www.zalora.sg" + product_links[i]
        items.append([title, price, image_url, product_url])

    print(f"✅ Page {page_num}: {len(title_tags)} products scraped.")
    time.sleep(random.uniform(3, 6))  # cooldown before next page

# ---------- Save to CSV ----------
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Price", "ImageURL", "ProductURL"])
    writer.writerows(items)

print(f"\n✅ Scraping complete. {len(items)} products saved to: {output_file}")


# 1245 pm 19 Jul
"""
Zalora uses PerimeterX bot protection, which detects:

The presence of navigator.webdriver = true

Missing chrome.runtime or other Chrome extensions

Unusual execution timing

Mouse/keyboard inactivity

Screen size or hardware mismatch

"""