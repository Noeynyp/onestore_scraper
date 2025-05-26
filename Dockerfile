FROM python:3.11-slim

# Install system dependencies required by Playwright Chromium
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils libu2f-udev libvulkan1 libxss1 libgtk-3-0 libx11-xcb1 libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install browsers
RUN python -m playwright install chromium

# Run your app
CMD ["python", "scraper_api.py"]
