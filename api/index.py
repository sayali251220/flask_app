'''from bs4 import BeautifulSoup
import requests as r
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Annotated

app = FastAPI()

#@app.get("/scrape")

@app.get("/scrape")
def scrap_meshoo(
    base_url: Annotated[str, Query(description="Base URL to scrape")],
    pages: Annotated[int, Query(1, description="Number of pages to scrape")]):
    all_class = [
        'sc-dkrFOg ProductListItem__GridCol-sc-1baba2g-0 dAbGbG kdQjpv',
        'sc-dkrFOg Pagestyled__ColStyled-sc-ynkej6-2 eSAbia rttYu',
        'sc-dkrFOg Pagestyled__ColStyled-sc-ynkej6-2 eSAbia rttYu'
    ]

    product = []
    prod_price = []
    reviews = []
    ratings = []

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Scraping page: {page}")
        response = r.get(url)
        html_data = response.content
        soup = BeautifulSoup(html_data, 'html.parser')

        for cls in all_class:
            for i in soup.find_all('div', {'class': cls}):
                try:
                    scrap_data = i.text.strip().split('₹', 1)
                    if len(scrap_data) == 2:
                        prod, rest_details = scrap_data
                        price, rate_rav_details = rest_details.split(' Free Delivery', 1)

                        product.append(prod.strip())
                        prod_price.append(price.strip())

                        if 'supplier' in rate_rav_details.lower():
                            ratings.append(rate_rav_details[:3])
                            reviews.append(0)

                        elif 'reviews' in rate_rav_details.lower():
                            rat_rv, _ = rate_rav_details.split(' ', 1)
                            rat = rat_rv[:3]
                            rv = rat_rv[3:]
                            reviews.append(rv)
                            ratings.append(rat)
                        else:
                            ratings.append('N/A')
                            reviews.append('N/A')
                except ValueError:
                    print("Error processing item:", i.text.strip())

    all_data = {
        'Scrap_time': datetime.now().isoformat(),
        'Product': product,
        'Price': prod_price,
        'Rating': ratings,
        'Reviews': reviews
    }

    return JSONResponse(content=all_data)'''

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from scraper import scrap_meshoo  # Importing from scraper.py

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI deployed successfully on Vercel!"}

@app.get("/scrape")
def scrape(
    base_url: str = Query(..., description="Base URL to scrape"),
    pages: int = Query(1, description="Number of pages to scrape")
):
    return scrap_meshoo(base_url, pages)