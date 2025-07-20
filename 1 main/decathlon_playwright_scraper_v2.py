import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv

OUTPUT_FILE = "decathlon_output.csv"
BASE_URL = "https://www.decathlon.sg/c/men/shoes.html"

async def main():
    items = []
    seen = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"🌐 Visiting: {BASE_URL}")
        await page.goto(BASE_URL)
        await page.wait_for_timeout(5000)

        max_rounds = 10
        round_count = 0

        while round_count < max_rounds:
            print(f"\n🔁 Scrape round {round_count + 1}/{max_rounds}")
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            product_cards = soup.select('a[href^="/p/"]')
            new_count = 0

            for card in product_cards:
                href = card.get("href")
                if not href or href in seen:
                    continue
                seen.add(href)
                product_url = "https://www.decathlon.sg" + href

                # Title
                title_div = card.select_one('div[title]')
                title = title_div.get("title", "").strip() if title_div else ""

                # Price
                price_span = card.select_one('span.vp-price-amount')
                price = price_span.text.strip() if price_span else ""

                # Image
                img_tag = card.select_one('img')
                image_url = img_tag.get("src", "").strip() if img_tag else ""

                if title:
                    items.append([title, price, image_url, product_url])
                    new_count += 1

            print(f"📦 Found {new_count} new products (total so far: {len(items)})")

            # Try clicking "View More"
            try:
                show_more_button = await page.query_selector('button[data-cy="Show-More"]')
                if show_more_button:
                    print(f"🔘 Clicking 'View More' ({round_count + 1})...")
                    await show_more_button.click()
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(3000)
                else:
                    print("✅ 'View More' button no longer visible.")
                    break
            except Exception as e:
                print(f"⚠️ Failed to click 'View More': {e}")
                break

            round_count += 1

        await browser.close()

    # Write to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "ImageURL", "ProductURL"])
        writer.writerows(items)

    print(f"\n✅ Done. Scraped {len(items)} Decathlon products to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())



"""
1350pm
only 12 prducts are scraped, so we need to click "View More" button until it is no longer visible.
But clicking view more, only 12 products are loaded each time, which means this usually happens because the DOM selectors are pulling from non-product or duplicate elements, or not all products load cleanly into the page even after clicks.

Let’s break it down and improve the scraping logic.



"""