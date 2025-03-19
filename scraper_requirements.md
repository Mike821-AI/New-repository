# Horizon Scanning Scraper Documentation


## Scraping Links

https://www.esma.europa.eu/press-news/esma-news
https://www.esma.europa.eu/databases-library/esma-library?f%5B0%5D=basic_%3A49
https://www.esma.europa.eu/news-publications/speeches
https://www.esma.europa.eu/databases-library/esma-library



## Overview
The **Horizon Scanning Scraper** is responsible for scraping regulatory websites to extract notices, speeches, newsletters, announcements, and similar updates. The extracted data is structured in JSON format, enabling automated monitoring and analysis of regulatory changes.

## Task Description
The scraper will:
1. Crawl designated government regulatory websites.
2. Identify and extract relevant publications such as news, announcements, speeches, and newsletters.
3. Capture key metadata about each document.
4. Store the extracted data in a standardized JSON format for further processing and analysis.

## JSON Data Structure
Each entry in the JSON output represents a single document (e.g., notice, announcement, newsletter) retrieved from a regulator's website. Below is the structure:

```json
[
    {
        "source_regulator": "FCA",
        "source_website": "www.esma.europa.eu",
        "retrieved_at": "2025-03-13T12:00:00Z",
        "id": "unique_identifier",
        "type": "news",
        "title": "FCA Announces New Safeguarding Rules",
        "url": "https://www.fca.org.uk/news/fca-announces-new-safeguarding-rules",
        "published_date": "2025-03-12",
        "HTML": "Full HTML of the document", 
        "related_documents": [
            {
                "title": "Consultation Paper CP23/10",
                "related_document_url": "https://www.fca.org.uk/publication/cp23-10.pdf"
            }
        ]
    }
]
```

### Field Definitions

#### `source_regulator` (String)
- The name of the regulatory authority issuing the document (e.g., FCA, SEC, ESMA).

#### `source_website` (String)
- The base URL of the regulatory authority's website.

#### `retrieved_at` (ISO 8601 Timestamp)
- The timestamp (UTC) when the document was retrieved by the scraper in the YYYY-MM-DDTHH:MM:SSZ format. 

#### `id` (String)
- A unique identifier for the document (generated via UUIDs to prevent duplicates).

#### `type` (String)
- The category of publication. Expected values include:
  - `news`
  - `announcement`
  - `speech`
  - `newsletter`
  - `consultation`
  - `policy_update`

#### `title` (String)
- The official title of the document.

#### `url` (String)
- The direct URL where the document is published on the regulator’s website.

#### `published_date` (ISO 8601)
- The publication date of the document as provided by the source in YYYY-MM-DD format. 

#### `HTML` (String)
- The full HTML content of the document, allowing for further text extraction and analysis.

#### `related_documents` (Array of Objects)
- A list of related documents referenced within the scraped document such as PDFs and any links to other  Each related document includes:
  - `title` (String): The title of the referenced document.
  - `related_document_url` (String): The direct URL to the referenced document.

## Scraping Considerations
- The scraper should handle pagination where applicable to ensure full retrieval of all documents.
- Some documents may require AJAX requests; the scraper should be able to fetch dynamically loaded content.
- PDFs or other non-HTML documents should be identified with links in the 'related_documents' array. 
- Error handling should be in place to manage cases where a document cannot be retrieved.

## Usage
- This data is expected to be ingested into an automated pipeline for regulatory monitoring and compliance tracking.
- The extracted HTML can be further processed to extract key insights via NLP techniques.
- The `related_documents` field allows analysts to track references and dependencies within regulatory publications.
