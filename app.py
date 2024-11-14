import os
import time
import requests
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
    product_name           = soup.find('h1', class_ = 'ui-pdp-title').get_text(strip=True)
    product_price: list    = soup.find_all('span', class_ = 'andes-money-amount__fraction')
    final_price: int       = int(product_price[0].get_text().replace(".", ""))
    installment_price: int = int(product_price[1].get_text().replace(".", ""))

    return {
        "product_name":      product_name,
        "final_price":       final_price,
        "installment_price":  installment_price
    }    

if __name__ == "__main__":
    while True:
        page_content = fetch_page()
        product_info = parse_page(page_content)
        print(product_info)
        time.sleep(10)