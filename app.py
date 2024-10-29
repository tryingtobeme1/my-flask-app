from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

app = Flask(__name__)

def fetch_ebay_listings(part_number=None, year=None, make=None, model=None, min_price=None, max_price=None):
    """Fetch eBay listings based on search criteria, prioritizing part number if provided."""
    base_url = "https://www.ebay.com/sch/i.html"

    if part_number:
        # If a part number is provided, use it as the main search term
        search_term = quote_plus(part_number)
    else:
        # Use year, make, and model if part number is not provided
        search_term = quote_plus(f"{year} {make} {model}")

    params = {
        '_from': 'R40',
        '_nkw': search_term,
        '_sacat': '6028',
        '_udlo': min_price,
        '_udhi': max_price,
        'LH_Complete': '1',
        'LH_Sold': '1',
        'rt': 'nc',
        'LH_ItemCondition': '4'
    }

    url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
        'Accept-Language': 'en-US',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('div.s-item__info')
        listings = []
        
        for item in items:
            title_elem = item.select_one('.s-item__title')
            price_elem = item.select_one('.s-item__price')
            date_elem = item.select_one('.s-item__ended-date')
            shipping_elem = item.select_one('.s-item__shipping')
            link_elem = item.select_one('a.s-item__link')
            
            if title_elem and price_elem:
                listings.append({
                    'Title': title_elem.text.strip(),
                    'Price': price_elem.text.strip(),
                    'Shipping': shipping_elem.text.strip() if shipping_elem else 'N/A',
                    'Date Sold': date_elem.text.replace('Sold', '').strip() if date_elem else 'N/A',
                    'Link': link_elem['href'] if link_elem else 'N/A'
                })
        return listings
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    part_number = request.form.get('part_number')
    year = request.form.get('year')
    make = request.form.get('make')
    model = request.form.get('model')
    min_price = request.form.get('min_price', '150')
    max_price = request.form.get('max_price', '700')
    
    listings = fetch_ebay_listings(part_number=part_number, year=year, make=make, model=model, min_price=min_price, max_price=max_price)
    return render_template('results.html', listings=listings)

if __name__ == '__main__':
    app.run(debug=True)
