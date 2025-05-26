from flask import Flask, jsonify
import requests
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def scrape_onestore():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://m.onestore.net/en-sg/main/main")

        # 🔍 Wait until .prod_item elements are present
        page.wait_for_selector('.prod_item')

        # Simulate scrolling to load more products
        for _ in range(5):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(1500)

        games = []
        products = page.query_selector_all('.prod_item')

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
        return games

@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    data = scrape_onestore()

    # Send the result to your n8n webhook
    webhook_url = "https://panisn.app.n8n.cloud/webhook/onestore-scraper"
    requests.post(webhook_url, json=data)

    return jsonify({"status": "success", "games_scraped": len(data)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
