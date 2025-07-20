import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
import random

OUTPUT_FILE = "shein_output.csv"
BASE_URL = "https://sg.shein.com/pdsearch/Shoes%20For%20Men/"


async def main():
    items = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"🌐 Visiting: {BASE_URL}")
        await page.goto(BASE_URL)
        await page.wait_for_timeout(random.randint(5000, 7000))

        # Scroll to load more products
        for _ in range(6):
            await page.mouse.wheel(0, 2500)
            await page.wait_for_timeout(1000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        product_cards = soup.select("a.goods-title-link")  # anchor wraps the product

        for card in product_cards:
            title = card.get("aria-label") or card.text.strip()
            price_tag = card.find_next("span", class_="normal-price-ctn__sale-price")
            price = price_tag.text.strip() if price_tag else ""

            # Get product URL
            link = card["href"]
            product_url = "https://sg.shein.com" + link if link.startswith("/") else link

            # Get image from parent div
            container = card.find_previous("div", class_="crop-image-container")
            image_url = ""
            if container and container.get("data-before-crop-src"):
                image_url = "https:" + container["data-before-crop-src"]

            items.append([title, price, image_url, product_url])

        await browser.close()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "ImageURL", "ProductURL"])
        writer.writerows(items)

    print(f"✅ Done. Scraped {len(items)} SHEIN products to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
