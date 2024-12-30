import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from whoosh.index import open_dir, create_in
from whoosh.fields import Schema, TEXT, ID
import os

def is_valid_url(url, base_domain):
    """Check if the URL belongs to the same domain."""
    return urlparse(url).netloc == base_domain

def crawl(start_url):
    """Crawl the website and collect content."""
    base_domain = urlparse(start_url).netloc
    visited = set()
    urls_to_visit = [start_url]
    data = []

    while urls_to_visit:
        url = urls_to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            visited.add(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            text = soup.get_text()

            data.append({"url": url, "title": title, "content": text})

            # Find all links on the page and add them to the URLs to visit
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if is_valid_url(full_url, base_domain):
                    urls_to_visit.append(full_url)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    return data

def create_index(data, index_dir="index"):
    """Index the crawled data using Whoosh."""
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    # Ensure the content field is stored
    schema = Schema(title=TEXT(stored=True), url=ID(stored=True), content=TEXT(stored=True))  # Make content stored=True

    if not os.path.exists(os.path.join(index_dir, "MAIN")):
        ix = create_in(index_dir, schema)
        print("Index created.")
    else:
        ix = open_dir(index_dir)
        print("Index opened.")
    
    writer = ix.writer()
    for item in data:
        print(f"Indexing: {item['title']}")  # Debugging line
        writer.add_document(title=item["title"], url=item["url"], content=item["content"])
    writer.commit()
    print("Indexing completed.")

if __name__ == "__main__":
    # Starting URL for crawling
    start_url = "https://vm009.rz.uos.de/crawl/index.html"  # Replace with your desired start URL
    # Crawl the website and collect data
    data = crawl(start_url)
    # Create or update the index with the crawled data
    create_index(data)
    print("Indexing completed.")
