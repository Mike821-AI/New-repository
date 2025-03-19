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
    "https://www.esma.europa.eu/databases-library/esma-library"
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
    
    # Get page source after JavaScript has rendered
    page_source = driver.page_source
    driver.quit()  # Close the browser session
    return page_source

# Function to extract data from ESMA pages using Selenium
def scrape_esma_page(url):
    indexes = []
    scraped_data = []
    scraped_data_filtered_type = []
    for i in range(0, 3):
        page_source = get_selenium_soup(url+'?page='+str(i))
        
        # Parse page content using BeautifulSoup
        soup = BeautifulSoup(page_source, "lxml")
        table = soup.find('table', class_='views-view-table')
        tbody = table.find('tbody')
        
        articles = tbody.find_all("tr")  # Adjust class as per ESMA website structure

        for article in articles:
            try:
                title_tag = article.find('td', class_="views-field-title").find('a')
                
                link = f"https://www.esma.europa.eu{title_tag['href']}" if title_tag and title_tag.get('href') else url

                id = generate_unique_id(link)
                
                title=title_tag.text

                date_tag = article.find("time")
                published_date = date_tag.text.strip() if date_tag else "Unknown"
                published_date = datetime.strptime(published_date, "%d/%m/%Y")
                if published_date < DATE_THRESHOLD:
                    print("This record was published before 2025-01-01 and will be excluded.")
                    continue
                else:
                    print("This record is after 2025-01-01 and will be included.")
                
                type = article.find('td', class_='views-field-field-document-type').text.strip()
                # Now, click the title link to open the detailed page
                detailed_data = scrape_detailed_article(link)

                # Collect the data
                document_data = {
                    "source_regulator": 'ESMA',
                    "source_website": "https://www.esma.europa.eu/databases-library/esma-library",
                    "retrieved_at": datetime.now().isoformat(),
                    "id": id,
                    "type": type,  # Default category, can be modified dynamically
                    "title": title.strip(),
                    "url": link,
                    "published_date": str(published_date),
                    "HTML": detailed_data['full_html'],
                    "related_documents": detailed_data['related_documents']
                }

                # If the document already exists in scraped_data, continue this roop
                if id in indexes:
                    continue
                scraped_data.append(document_data)
                indexes.append(id)

                if document_data['type'] == 'Press Release':
                    scraped_data_filtered_type.append(document_data) 

            except Exception as e:
                print(f"Error extracting data from {url}: {e}")

    return scraped_data, scraped_data_filtered_type

# Function to scrape the detailed article page after clicking the title
def scrape_detailed_article(url):
    driver = get_driver()
    driver.get(url)
    # time.sleep(1)  # Wait for the page to load completely

    # Scraping the detailed content of the article page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")

    detailed_data = {}

    detailed_data['full_html'] = str(soup.find('article', class_='node--view-mode-full'))

    related_document = {}
    document = soup.find('article', class_='media--view-mode-full')
    related_document['title'] = document.find('div', class_='field--name-field-document-title').text.strip()
    related_document['related_document_url'] = f"https://www.esma.europa.eu{document.find('a').get('href')}"

    detailed_data['related_documents'] = [related_document]

    driver.quit()  # Close the browser session
    # return detailed_data
    return detailed_data

# Function to scrape all ESMA pages
def scrape_all_esma_pages():
    all_data = []
    all_data_filtered_type = []
    for url in SCRAPING_URLS:
        print(f"Scraping: {url}")
        page_data, page_data_filtered_type = scrape_esma_page(url)
        all_data.extend(page_data)
        all_data_filtered_type.extend(page_data_filtered_type)

    # Save data to JSON file
    with open("esma_scraped_all_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete! {len(all_data)} records saved.")

    # Save data to JSON file
    with open("esma_scraped_documents_filtered_type_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data_filtered_type, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete! {len(all_data)} records saved.")

# Execute the scraper
if __name__ == "__main__":
    scrape_all_esma_pages()
