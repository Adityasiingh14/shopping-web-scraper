import requests
from bs4 import BeautifulSoup

def makeInt(s):
    i = ""

    for ch in [c for c in s]:
        if ch == "." and i:
            break

        if not ch.isdigit():
            continue

        i += ch

    return int(i)

def fetch_html(source, headers={}):
    response = requests.get(source, headers=headers)

    while response.status_code != 200:
        response = requests.get(source, headers=headers)

    return response.text

def scrape_html(html, scrape_data):
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find_all(
        *scrape_data["item-query"][0],
        **scrape_data["item-query"][1]
    )

    output = []

    for result in search_results:
        result_name = result.find(
            *scrape_data["item-name"][0],
            **scrape_data["item-name"][1]
        )

        result_price = result.find(
            *scrape_data["item-price"][0],
            **scrape_data["item-price"][1]
        )

        result_link = result.find(
            "a",
            href=True
        )

        if not all([result_name, result_price, result_link]):
            continue

        output.append({
            "source": scrape_data["source"],
            "name": result_name.get_text(),
            "price": result_price.get_text(),
            "link": result_link.href
        })
    
    return output

def scrape(url, headers, scrape_data):
    html = fetch_html(url, headers)
    output = scrape_html(html, scrape_data)

    return output

def search(query, websites, headers):
    output = []

    for website in websites:
        output.extend(
            scrape(
                website["url"] + query,
                headers,
                website["scrape_data"]
            )
        )
    
    output.sort(key=lambda res: makeInt(res["price"]))
    
    return output

def display_results(results):
    for result in results:
        results_name = result["name"][:30]
        
        results_price = makeInt(result["price"])
        results_price = f"Rs. {results_price}"

        results_link = result["link"]
        results_source = result["source"]

        f_results = f"{results_name:<30} - {results_price:<20} - {results_source}"

        print(f_results)

def cli(websites, headers):
    query = input("Search for: ")
    if not query:
        return False
    
    results = search(query, websites, headers)
    display_results(results)

    return True

if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    websites_data = [
        {
            "url": "https://amazon.in/s?k=",
            "scrape_data": {
                "item-query": [
                    ["div"],
                    {"class": "s-result-item"}
                ],
                "item-name": [
                    ["span"],
                    {"class": "a-text-normal"}
                ],
                "item-price": [
                    ["span"],
                    {"class": "a-offscreen"}
                ],
                "source": "Amazon"
            }
        },
        {
            "url": "https://snapdeal.com/search?keyword=",
            "scrape_data": {
                "item-query": [
                    ["div"],
                    {"class": "product-tuple-listing"}
                ],
                "item-name": [
                    ["p"],
                    {"class": "product-title"}
                ],
                "item-price": [
                    ["span"],
                    {"class": "product-price"}
                ],
                "source": "Snapdeal"
            }
        }
    ]

    while cli(websites_data, headers):
        pass

