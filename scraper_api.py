from flask import Flask, jsonify
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def scrape_onestore():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Set a realistic user agent for better compatibility
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/115.0 Safari/537.36"
                )
            )
            page = context.new_page()

            logging.info("Navigating to main page...")
            page.goto("https://m.onestore.net/en-sg/main/main", timeout=60000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            # Scroll slowly to load lazy content
            for i in range(5):
                logging.info(f"Scrolling... step {i+1}/5")
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)

            logging.info("Selecting product elements...")
            products = page.query_selector_all('.swiper-slide')

            game_urls = []
            for product in products:
                link = product.query_selector('a.swiper-slide-link')
                if link:
                    href = link.get_attribute('href')
                    if href and not href.startswith('javascript:void(0)'):
                        full_url = "https://m.onestore.net" + href
                        game_urls.append({"url": full_url})

            context.close()
            browser.close()

            logging.info(f"Scraped {len(game_urls)} game URLs")
            return game_urls

    except PlaywrightTimeoutError as e:
        logging.error(f"Timeout error during scraping: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        return []

@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    data = scrape_onestore()

    webhook_url = "https://panisn.app.n8n.cloud/webhook-test/onestore-scraper"

    try:
        resp = requests.post(webhook_url, json=data)
        resp.raise_for_status()
        logging.info("Data sent to webhook successfully.")
    except Exception as e:
        logging.error(f"Failed to send data to webhook: {e}")

    return jsonify({"status": "success", "urls_scraped": len(data)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
