import time
import sqlite3
import atexit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up database
def setup_database():
    connection = sqlite3.connect('listings.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            length REAL,
            chest REAL,
            price REAL,
            market TEXT,
            designer TEXT,
            url TEXT
        )
    """)
    return connection, cursor

# Set up webdriver
def setup_webdriver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "normal"
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(1)
    return driver

# Get user requirements
def get_user_input():
    min_chest = float(input("Enter minimum chest measurement in inches: "))
    max_chest = float(input("Enter maximum chest measurement in inches: "))
    min_length = float(input("Enter minimum length measurement in inches: "))
    max_length = float(input("Enter maximum length measurement in inches: "))
    min_price = float(input("Enter minimum price: "))
    max_price = float(input("Enter maximum price: "))
    return min_chest, max_chest, min_length, max_length, min_price, max_price

# Get user category + link to category
def get_category():
    categories = {
        1: "T-shirts (short sleeve)",
        2: "T-shirts (long sleeve)",
        3: "Polos",
        4: "Sweaters",
        5: "Button-ups",
        6: "Hoodies",
        7: "Tank tops",
        8: "Jackets"
    }
    
    links = {
        1: "https://www.grailed.com/categories/short-sleeve-t-shirts",
        2: "https://www.grailed.com/categories/long-sleeve-t-shirts",
        3: "https://www.grailed.com/categories/polos",
        4: "https://www.grailed.com/categories/sweaters-knitwear",
        5: "https://www.grailed.com/categories/shirts-button-ups",
        6: "https://www.grailed.com/categories/sweatshirts-hoodies",
        7: "https://www.grailed.com/categories/tank-tops-sleeveless",
        8: "https://www.grailed.com/categories/outerwear"
    }

    print("Categories:")
    for key, value in categories.items():
        print(f"{key}: {value}")
    
    choice = int(input("Choose a category to search: "))
    return links.get(choice, links[1]), categories.get(choice, categories[1])

# Extract measurements
def extract_measurement(text):
    try:
        return float(text.split(' ')[0])
    except ValueError:
        return None

# Extract price
def extract_price(text):
    try:
        return float(text.replace('$', '').replace(',', ''))
    except ValueError:
        return None

# Check measurements against user requirements
def check_measurements(url, min_chest, max_chest, min_length, max_length, min_price, max_price, cursor, category, driver):
    # Assure the new tabs do not progress
    if '/similar' in url:
        return None
    
    original_window = driver.current_window_handle
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    
    try:
        chest_measurement = WebDriverWait(driver, 0).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[1]/div[2]"))
        ).text
        length_measurement = WebDriverWait(driver, 0).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[1]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div[2]"))
        ).text
        price_element = WebDriverWait(driver, 0).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[1]/div[2]/div[1]/div[3]/div/span"))
        )
        price = extract_price(price_element.text)
        market_element = WebDriverWait(driver, 0).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[1]/div[2]/div[2]/div[2]/div[7]/div[1]/span[1]"))
        )
        market = market_element.text.replace("Posted in ", "")
        designer = WebDriverWait(driver, 0).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[1]/div[2]/div[1]/div[2]/p[1]/a"))
        ).text

        # extract measurements
        chest = extract_measurement(chest_measurement)
        length = extract_measurement(length_measurement)

        # check requirements
        if chest and length and min_chest <= chest <= max_chest and min_length <= length <= max_length and min_price <= price <= max_price:
            # if it fits, insert into database
            cursor.execute(
                "INSERT INTO listings (length, chest, price, market, designer, url, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (length, chest, price, market, designer, url, category)
            )
            return f"Length: {length}, Chest: {chest}, Price: ${price}, Market: {market}, Designer: {designer}, Link: {url}"
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Could not retrieve measurements for {url}: {e}")
    finally:
        driver.close()
        driver.switch_to.window(original_window)
    
    return None

# scroll page to load new listings
def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def main():
    driver = setup_webdriver()
    connection, cursor = setup_database()

    # commit database when terminating
    atexit.register(lambda: (connection.commit(), connection.close(), print("Database changes committed and connection closed.")))

    # get user input
    url, category = get_category()
    min_chest, max_chest, min_length, max_length, min_price, max_price = get_user_input()
    
    driver.get(url)
    time.sleep(3)

    # track links checked, amount found, and scroll count
    processed_urls = set()
    matching_count = 0
    max_scrolls = 1000
    scroll_count = 0

    while scroll_count < max_scrolls:
        # allow links to load
        links = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="feed-item"]//a'))
        )
        # get listings urls
        urls = [link.get_attribute('href') for link in links if '/listings/' in link.get_attribute('href')]

        # no more urls available
        if not urls:
            print("No more new listings found. Exiting.")
            break
        

        for url in urls:
            # ensure url has not been processed before
            if url not in processed_urls:
                result = check_measurements(url, min_chest, max_chest, min_length, max_length, min_price, max_price, cursor, category, driver)
                if result:
                    matching_count += 1
                    # print to terminal to monitor progress
                    print(f"Found matching listing: {result}")
                processed_urls.add(url)

        scroll_page(driver)
        scroll_count += 1

    driver.quit()
    print(f"Found {matching_count} matching listings. Results saved to the database.")

if __name__ == '__main__':
    main()
