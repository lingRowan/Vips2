import requests
from bs4 import BeautifulSoup



urls = "https://vm009.rz.uos.de/crawl/index.html"
start_url = urls+'home.html'
agenda = [start_url]

while agenda:
        current_url = agenda.pop()
        response = requests.get(current_url)
        if response.status_code == 200:
              soup = BeautifulSoup(response.content, "html.parser")
              link_elements = soup.find_all("Australia")
              print(link_elements)
  