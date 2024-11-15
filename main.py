import os
import time
import asyncio
import sqlite3
import requests
import pandas as pd
from telegram import Bot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram bot settings
TOKEN   = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot     = Bot(token=TOKEN)

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

def create_connection(database_name='macbook_pro_prices.db'):
    """Creates a connection to the SQLite3 Database"""
    conn = sqlite3.connect(database_name)
    return conn

def setup_database(conn):
    """Creates the price table if it does not exist"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS macbook_pro_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        final_price INTEGER,
        installment_price INTEGER,
        max_price INTEGER,
        min_price INTEGER,
        uptaded_at TEXT
        )
    ''')
    conn.commit()

def save_to_dataframe(product_info, df):
    """Appends product information, including max and min prices, to a DataFrame and returns it"""
    new_row = pd.DataFrame([product_info])
    df = pd.concat([df, new_row], ignore_index=True)
    return df

# Function to save data to the database
def save_to_database(conn, product_info):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(final_price), MIN(final_price) FROM macbook_pro_prices")
    max_price, min_price = cursor.fetchone()
    current_price = product_info['final_price']
    max_price = max(current_price, max_price or current_price)
    min_price = min(current_price, min_price or current_price)
    product_info['max_price'] = max_price
    product_info['min_price'] = min_price
    cursor.execute('''
        INSERT INTO macbook_pro_prices (product_name, final_price, installment_price, uptaded_at, max_price, min_price)
        VALUES (:product_name, :final_price, :installment_price, :uptaded_at, :max_price, :min_price)
    ''', product_info)
    conn.commit()
    return max_price, min_price  # Return max and min prices

async def send_telegram_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

# Main function
async def main():
    conn = create_connection()
    setup_database(conn)
    df = pd.DataFrame()

    # Initialize an empty DataFrame to store data for the CSV file
    df = pd.DataFrame()
    
    while True:
        
        # Fetch and parse the page content
        page_content = fetch_page()
        product_info = parse_page(page_content)
        
        # Save to database
        save_to_database(conn, product_info)

        # Save to DataFrame
        df = save_to_dataframe(product_info, df)
        
        # Save to CSV file
        df.to_csv("macbook_pro_prices.csv")
        
        # Print DataFrame and confirmation message
        print(df)
        print(f"Data {product_info} saved in the Database and CSV successfully!")

        # Send Telegram message with max and min prices
        await send_telegram_message(f"The maximum price is: {max_price}, and the minimum price is: {min_price}")
        
        # Pause execution for 10 seconds before the next loop iteration
        await asyncio.sleep(10)

asyncio.run(main())