import json
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup

# List of target URLs for scraping ESMA regulatory updates
SCRAPING_URLS = [
    "https://www.esma.europa.eu/press-news/esma-news"
]

# Define the date threshold (YYYY-MM-DD)
DATE_THRESHOLD = datetime(2025, 1, 1)

# Function to generate unique ID
def generate_unique_id(url):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

# Set up Selenium WebDriver
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(options=chrome_options)  # Ensure chromedriver is in your PATH
    return driver

# Function to fetch and parse content using Selenium
def get_selenium_soup(url):
    driver = get_driver()
    driver.get(url)
    
    # Wait for JavaScript to load content
    # time.sleep(1)  # Adjust sleep time if necessary for the page to load completely
    
    # Get page source after JavaScript has rendered
    page_source = driver.page_source
    driver.quit()  # Close the browser session
    return page_source

# Function to extract data from ESMA pages using Selenium
def scrape_esma_page(url):
    page_source = get_selenium_soup(url)
    
    # Parse page content using BeautifulSoup
    soup = BeautifulSoup(page_source, "lxml")
    
    articles = soup.find_all("div", class_="news-contentcard")  # Adjust class as per ESMA website structure
    scraped_data = []

    for article in articles:
        try:
            title_tag = article.find("a")
            link = f"https://www.esma.europa.eu{title_tag['href']}" if title_tag and title_tag.get('href') else url

            date_tag = article.find("div", class_="search-date")
            published_date = date_tag.text.strip() if date_tag else "Unknown"

            # Now, click the title link to open the detailed page
            detailed_data = scrape_detailed_article(link)

            # Collect the data
            document_data = {
                "source_regulator": 'ESMA',
                "source_website": "www.esma.europa.eu",
                "retrieved_at": datetime.now().isoformat(),
                "id": generate_unique_id(link),
                "type": "news",  # Default category, can be modified dynamically
                "title": detailed_data['article_title'],
                "url": link,
                "published_date": published_date,
                "HTML": detailed_data['full_html'],
                "related_documents": detailed_data['related_documents']
            }

            scraped_data.append(document_data)

        except Exception as e:
            print(f"Error extracting data from {url}: {e}")

    return scraped_data

# Function to scrape the detailed article page after clicking the title
def scrape_detailed_article(url):
    driver = get_driver()
    driver.get(url)
    # time.sleep(1)  # Wait for the page to load completely

    # Scraping the detailed content of the article page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")

    detailed_data = {}
    related_documents = []

    detailed_data['article_title'] = soup.find("span", class_="field--name-title").text

    # regulator_container = soup.find("div", class_="field__item")
    # detailed_data['source_regulator'] = regulator_container.find('a').text
    detailed_data['full_html'] = str(soup.find('article'))

    documents = soup.findAll('td', class_='views-field-title')
    for document in documents:
        related_document = {}
        related_document['title'] = document.find('span').text
        related_document['related_document_url'] = f"https://www.esma.europa.eu{document.find('a').get('href')}"
        related_documents.append(related_document)
    detailed_data['related_documents'] = related_documents

    driver.quit()  # Close the browser session
    # return detailed_data
    return detailed_data

# Function to scrape all ESMA pages
def scrape_all_esma_pages():
    all_data = []
    for url in SCRAPING_URLS:
        print(f"Scraping: {url}")
        page_data = scrape_esma_page(url)
        all_data.extend(page_data)

    # Save data to JSON file
    with open("esma_scraped_news_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete! {len(all_data)} records saved.")

# Execute the scraper
if __name__ == "__main__":
    scrape_all_esma_pages()
