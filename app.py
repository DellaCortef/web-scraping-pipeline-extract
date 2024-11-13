import os
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
    product_name  = soup.find('h1', class_ = 'ui-pdp-title').get_text(strip=True)
    #product_price = 
    print(product_name)
    

if __name__ == "__main__":
    page_content = fetch_page()
    parse_page(page_content)
