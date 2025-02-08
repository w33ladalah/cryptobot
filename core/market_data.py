import requests
from config.settings import COINGECKO_API

def get_price(token_id):
    url = f"{COINGECKO_API}/simple/price?ids={token_id}&vs_currencies=usd"
    return requests.get(url).json()

# Example usage
print(get_price("ethereum"))
