from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from typing import Annotated, Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI deployed successfully!"}

@app.get("/scrape")
def scrap_meshoo(
    base_url: Annotated[str, Query(description="Base URL to scrape")],
    pages: Annotated[int, Query(1, description="Number of pages to scrape")],
    limit: Optional[int] = Query(None, description="Limit the number of products scraped")
) -> Dict:
    all_class = [
        'sc-dkrFOg ProductListItem__GridCol-sc-1baba2g-0 dAbGbG kdQjpv',
        'sc-dkrFOg Pagestyled__ColStyled-sc-ynkej6-2 eSAbia rttYu'
    ]

    product, prod_price, ratings, reviews = [], [], [], []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        logging.info(f"Scraping page: {page} → {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.warning(f"Request failed for page {page}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        for cls in all_class:
            for i in soup.find_all('div', {'class': cls}):
                try:
                    scrap_data = i.text.strip().split('₹', 1)
                    if len(scrap_data) == 2:
                        prod, rest_details = scrap_data
                        price, *details = rest_details.split(' Free Delivery', 1)

                        product.append(prod.strip())
                        prod_price.append(price.strip())

                        details_text = details[0] if details else ""

                        if 'supplier' in details_text.lower():
                            ratings.append(details_text[:3])
                            reviews.append("0")
                        elif 'reviews' in details_text.lower():
                            parts = details_text.split()
                            ratings.append(parts[0] if len(parts) >= 1 else "N/A")
                            reviews.append(parts[1] if len(parts) >= 2 else "N/A")
                        else:
                            ratings.append("N/A")
                            reviews.append("N/A")

                        if limit and len(product) >= limit:
                            break
                except Exception as e:
                    logging.error(f"Error processing item: {e}")

            if limit and len(product) >= limit:
                break

    # Create DataFrame for future use or export
    df = pd.DataFrame({
        "Product": product,
        "Price": prod_price,
        "Rating": ratings,
        "Reviews": reviews
    })

    data = {
        'Scrap_time': datetime.now().isoformat(),
        'Total_products': len(df),
        'Data': df.to_dict(orient="records")
    }

    return JSONResponse(content=data)
