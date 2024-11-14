import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# creating function to request necessarily information
def fetch_page():
    url = os.getenv("PRODUCT_URL")
    response = requests.get(url)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Extract product name
    product_name = soup.find('h1', class_='ui-pdp-title').get_text(strip=True)
    
    # Extract prices
    product_price = soup.find_all('span', class_ = 'andes-money-amount__fraction')
    
    # Check if product_price has at least one element
    final_price = int(product_price[0].get_text().replace(".", "")) if len(product_price) > 0 else None
    
    # Check if product_price has at least two elements for installment price
    installment_price = int(product_price[1].get_text().replace(".", "")) if len(product_price) > 1 else None
    
    # Get current time
    uptaded_at = time.strftime('%Y-%m-%d %H:%M:%S')

    return {
        "product_name":      product_name,
        "final_price":       final_price,
        "installment_price":  installment_price,
        "uptaded_at": uptaded_at
    }

def save_to_dataframe(product_info, df):
    new_row = pd.DataFrame([product_info])
    df = pd.concat([df, new_row], ignore_index=True)
    return df

if __name__ == "__main__":
    
    df = pd.DataFrame()
    
    while True:
        page_content = fetch_page()
        product_info = parse_page(page_content)
        df = save_to_dataframe(product_info, df)
        print(df)
        time.sleep(10)