# Price Monitoring with Web Scraping and Telegram Notifications

This project monitors product prices on e-commerce sites. Using web scraping techniques, the project collects prices and sends notifications on Telegram when the value reaches a specific limit defined by the user. The application is modular, divided into parts to facilitate development and maintenance.

```mermaid
sequenceDiagram
    participant User as user
    participant Bot as Bot telegram_bot
    participant Script as principal_script
    participant DB as sqlline_database
    participant ML as mercado_livre

    User->>Script: Start the script
    Script->>ML: fetch_page() - Request to get page HTML
    ML-->>Script: Responds with page HTML

    Script->>Script: parse_page() - Extracts price and product information
    Script->>DB: create_connection() - Connects to the database
    Script->>DB: setup_database() - Creates table 'prices' if it does not exist
    Script->>DB: get_max_price() - Query highest recorded price

    alt If there is no registered price
        Script->>Bot: send_telegram_message() - "New higher price detected"
        Bot-->>User: Notification via Telegram
    else If there is a registered price
        Script->>Script: Compare the current price with the highest recorded price
        alt If current price is higher
            Script->>Bot: send_telegram_message() - "New higher price detected"
            Bot-->>User: Notification via Telegram
        else If the current price is not higher
            Script->>Bot: send_telegram_message() - "Highest recorded price is X"
            Bot-->>User: Notification via Telegram
        end
    end

    Script->>DB: save_to_database() - Saves price and product information
    Script->>Script: Wait 10 seconds before repeating the process
    loop Loop continuous
        Script->>ML: Request to update price
        ML-->>Script: Reply with new price
        Script->>Script: Verification and notification process repeats
    end
```

## Libraries Used and Explanation

1. **requests**: Used to make HTTP requests and obtain the HTML of web pages.
2. **BeautifulSoup (bs4)**: Used to analyze and extract specific information from the HTML of pages, such as the price of the product.
3. **schedule**: Library for scheduling tasks, allowing you to check prices at regular intervals.
4. **pandas**: Facilitates data manipulation, allowing you to save and load price histories in CSV files.
5. **sqlite3**: A lightweight SQLite database used to store and organize price data over time.
6. **python-telegram-bot**: Library for sending messages to Telegram, notifying the user when the price reaches a specific value.
7. **python-dotenv**: Loads environment variables from a `.env` file, where sensitive information such as the Telegram token and chat ID is stored.

## Prerequisites

1. **Python 3.6+**: Make sure you have Python 3.6 or higher installed.
2. **Dependencies**: Install the libraries listed in the `requirements.txt` file.

To install dependencies, run the command:
```bash
pip install -r requirements.txt 
```

## Application Structure

### `app_1`: Data Collector with `requests`
This module makes HTTP requests to access the HTML content of product pages. It collects the raw HTML that will be processed by `app_2`.

### `app_1`: HTML parser with `BeautifulSoup`
This module receives the HTML from `app_1` and uses `BeautifulSoup` to extract specific information, such as the current price of the product.

### `app_1`: Task Scheduling with `schedule`
This module uses `schedule` to define how frequently price monitoring is performed. For example, it can be configured to check the price every 10 minutes.

### `app_2`: Data Manipulation with `pandas`
This module organizes collected data and can save price history to a CSV file for easier analysis and storage.

### `app_3`: Database with `sqlite3`
This module manages the SQLite database, creating tables and storing price history information.

### `app_4`: Price Comparison (`max_price`)
This module compares the current price of the product with the user-defined `max_price`. If the price is below the limit, it sends a notification using `app_7`.

### `app_5`: Sending Notification with Telegram
This module uses the `python-telegram-bot` library to send a message to Telegram informing that the price has reached the desired value.