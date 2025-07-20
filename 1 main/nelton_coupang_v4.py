import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
import random

OUTPUT_FILE = "zalora_playwright_output.csv"
BASE_URL = "https://www.zalora.sg/c/men/shoes/c-27?page="
MAX_PAGES = 3


async def scrape_page(page, url):
    await page.goto(url)
    await page.wait_for_timeout(random.randint(5000, 9000))  # wait 5–9s
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    if soup.select_one(".px-captcha-container"):
        print(f"🚫 CAPTCHA detected on {url}. Skipping...")
        return []

    titles = soup.select('[data-test-id="productTitle"]')
    prices = soup.select("span.font-bold.text-base")
    images = soup.select('img[alt]')
    links = [a["href"] for a in soup.select('a[href^="/"]') if "/p/" in a["href"]]
    links = list(dict.fromkeys(links))

    items = []
    for i in range(min(len(titles), len(prices), len(images), len(links))):
        title = titles[i].text.strip()
        price = prices[i].text.strip().replace("S$", "SGD")
        image = images[i].get("src")
        product_url = "https://www.zalora.sg" + links[i]
        items.append([title, price, image, product_url])

    print(f"✅ Scraped {len(items)} items from {url}")
    return items


async def main():
    all_items = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for i in range(1, MAX_PAGES + 1):
            url = BASE_URL + str(i)
            print(f"🌐 Visiting: {url}")
            items = await scrape_page(page, url)
            all_items.extend(items)
            await page.wait_for_timeout(random.randint(3000, 5000))  # cooldown

        await browser.close()

    # Save to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "ImageURL", "ProductURL"])
        writer.writerows(all_items)

    print(f"\n✅ Done. Saved {len(all_items)} items to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())



# 1320 pm 19 Jul
"""
Thanks for testing it — and wow, Zalora's bot detection is seriously aggressive. Even Playwright — which is usually stealthy enough for most modern e-commerce sites — is being flagged instantly on all pages. Here's what this means and your options:



"""