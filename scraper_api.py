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
            page = browser.new_page()

            logging.info("Navigating to main page...")
            page.goto("https://m.onestore.net/en-sg/main/main", timeout=60000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            # Scroll slowly to trigger lazy loading
            for i in range(5):
                logging.info(f"Scrolling... step {i+1}/5")
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(2000)

            logging.info("Selecting product elements...")
            products = page.query_selector_all('.prod_item')

            games = []
            for product in products:
                title = product.query_selector('.prod_name')
                price = product.query_selector('.price .current')
                discount = product.query_selector('.price .discount')

                games.append({
                    "title": title.inner_text().strip() if title else "",
                    "price": price.inner_text().strip() if price else "",
                    "discount": discount.inner_text().strip() if discount else ""
                })

            browser.close()
            logging.info(f"Scraped {len(games)} games")
            return games

    except PlaywrightTimeoutError as e:
        logging.error(f"Timeout error during scraping: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error during scraping: {e}")
        return []


@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    data = scrape_onestore()

    webhook_url = "https://panisn.app.n8n.cloud/webhook/onestore-scraper"
    try:
        resp = requests.post(webhook_url, json=data)
        resp.raise_for_status()
        logging.info("Data sent to webhook successfully.")
    except Exception as e:
        logging.error(f"Failed to send data to webhook: {e}")

    return jsonify({"status": "success", "games_scraped": len(data)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
