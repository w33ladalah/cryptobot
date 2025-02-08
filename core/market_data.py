from devtools import debug
from datetime import datetime
import pytz
from config.settings import config
import pandas as pd
import httpx


def get_historical_data(token_id, days=30):
    """
    Fetch historical prices from CoinGecko.
    :param token_id: Token ID (e.g., 'ethereum', 'bitcoin')
    :param days: Number of days to fetch data for
    :return: List of dictionaries with date & price
    """
    url = f"{config.COINGECKO_API}/coins/{token_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
    response = httpx.get(url)
    data = response.json()

    return [{"date": item[0], "price": item[1]} for item in data.get("prices", [])]


def get_dexscreener_data(chain, pair_address):
    """
    Fetch real-time data from DexScreener
    :param chain: Blockchain network (e.g., 'ethereum', 'bsc')
    :param pair_address: Token pair address (e.g., '0xTokenAddressHere')
    :return: Dictionary with price, liquidity, and 1h price change
    """
    url = f"{config.DEXSCREENER_API}/{chain}/{pair_address}"
    response = httpx.get(url)
    data = response.json()

    if 'pairs' in data and len(data['pairs']) > 0:
        price_change = data['pairs'][0]["priceChange"]
        return {
            "price": float(data['pairs'][0]["priceUsd"]),
            "liquidity": float(data['pairs'][0]["liquidity"]["usd"]),
            "price_change_1h": float(price_change.get("h1", price_change.get("h6", price_change.get("h24", 0))))
        }
    return None


def combine_data(historical_data, real_time_data):
    """
    Combine historical data from CoinGecko and real-time data from DexScreener.
    :return: Processed DataFrame
    """
    df = pd.DataFrame(historical_data)
    df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.utc).strftime('%Y-%m-%d'))
    # df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(x / 1000, datetime.timezone.utc).strftime('%Y-%m-%d'))

    if real_time_data:
        df["price_now"] = real_time_data["price"]
        df["liquidity"] = real_time_data["liquidity"]
        df["price_change_1h"] = real_time_data["price_change_1h"]
    else:
        df["price_now"] = None
        df["liquidity"] = None
        df["price_change_1h"] = None

    return df


if __name__ == "__main__":
    historical_data = get_historical_data("ethereum")
    debug(historical_data)

    dexscreener_data = get_dexscreener_data("solana", "f52fc4hp6w6vglcdhewe2qdjsce1wzqlt33dzupqdcza")
    debug(dexscreener_data)
