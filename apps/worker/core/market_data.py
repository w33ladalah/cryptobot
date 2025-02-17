from config.settings import config
from datetime import datetime
from devtools import debug
from typing import Optional, Dict, List
import httpx
import pandas as pd
import pytz


def get_historical_data(token_id: str, days: int = 30) -> List[Dict[str, float]]:
    """
    Retrieves historical market data for a specified token.

    Args:
        token_id (str): The identifier for the token.
        days (int, optional): The number of days to look back. Defaults to 30.

    Returns:
        List[Dict[str, float]]: A list of dictionaries containing "date" and "price".
            - "date": The date string in ISO format.
            - "price": The price value for that day.

    Note:
        Returns None if no data is found for the specified token.
    """

    headers = {
        "Authorization": f"Bearer {config.COINGECKO_API_KEY}"
    }
    url = f"{config.COINGECKO_API}/coins/{token_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
    response = httpx.get(url, headers=headers)
    data = response.json()

    return [{"date": item[0], "price": item[1]} for item in data.get("prices", [])]


def get_realtime_data(chain: str, pair_address: str) -> Optional[Dict[str, float]]:
    """
    Retrieves DEXScreener's data for a given chain and address.

    Args:
        chain (str): The chain identifier.
        pair_address (str): The address of the specific pair.

    Returns:
        Dict[str, float]: A dictionary containing price, liquidity, and price change metrics.
            - "price": The bid/ask price in USD.
            - "liquidity": Liquidity value in USD.
            - "price_change_1h": Price change from 1 hour ago in USD.

    Note:
        Returns None if no data is found for the specified pair.
    """

    url = f"{config.DEXSCREENER_API}/pairs/{chain}/{pair_address}"
    response = httpx.get(url)
    data = response.json()

    if 'pairs' in data and len(data['pairs']) > 0:
        price_change = data['pairs'][0]["priceChange"]
        return {
            "price": float(data['pairs'][0]["priceUsd"]),
            "liquidity": float(data['pairs'][0]["liquidity"]["usd"]),
            "price_change_1h": float(price_change.get("h1", 0)),
        }
    return None


def get_platforms() -> List[Dict[str, str]]:
    """
    Fetches a list of cryptocurrency platforms from the CoinGecko API.
    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing the name of the cryptocurrency
        and its corresponding Ethereum platform address.
    Raises:
        Exception: If there is an error while making the HTTP request or processing the response.
    """

    try:
        response = httpx.get(f"{config.COINGECKO_API}/coins/list?include_platform=true")
        response.raise_for_status()
        data = response.json()
        return [{"name": item["name"], "address": item["platforms"]["ethereum"]} for item in data]
    except Exception as e:
        raise Exception(str(e))


def search_token_pairs(query: str) -> List[Dict[str, any]]:
    """
    Searches for token pairs matching the given query using the DEX Screener API.
    Args:
        query (str): The search query string.
    Returns:
        List[Dict[str, any]]: A list of dictionaries containing token pair information.
    Raises:
        Exception: If there is an error during the API request or response processing.
    """

    try:
        response = httpx.get(f"{config.DEXSCREENER_API}/search/?q={query}".replace("/pairs/", "/"))
        response.raise_for_status()
        data = response.json()
        return data.get("pairs", [])
    except Exception as e:
        raise Exception(str(e))


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for a given DataFrame containing market data.
    This function adds three new columns to the input DataFrame:
    - Simple Moving Average (SMA) over a 14-day window
    - Exponential Moving Average (EMA) over a 14-day window
    - Volatility as the standard deviation of percentage change over a 14-day window
    Args:
        df (pd.DataFrame): DataFrame containing market data with a 'price' column.
    Returns:
        pd.DataFrame: DataFrame with additional columns for SMA, EMA, and Volatility.
    """


    df["SMA_14"] = df["price"].rolling(window=14).mean()
    df["EMA_14"] = df["price"].ewm(span=14, adjust=False).mean()
    df["Volatility"] = df["price"].pct_change().rolling(14).std()

    return df


def combine_data(historical_data: Optional[pd.DataFrame], real_time_data: Optional[pd.DataFrame]):
    """
    Combines historical and real-time market data into a single DataFrame.
    This function takes historical market data and real-time market data, processes the historical data to include
    calculated indicators, and merges the real-time data into the historical data DataFrame. If real-time data is not
    provided, the resulting DataFrame will have None values for the real-time data columns.
    Args:
        historical_data (Optional[pd.DataFrame]): A DataFrame containing historical market data.
        real_time_data (Optional[pd.DataFrame]): A DataFrame containing real-time market data.
    Returns:
        pd.DataFrame: A DataFrame containing the combined historical and real-time market data.
    Example:
        historical_data = pd.DataFrame({
            'date': [1625097600000, 1625184000000],
            'open': [34000, 35000],
            'high': [35000, 36000],
            'low': [33000, 34000],
            'close': [34500, 35500],
            'volume': [1000, 1500]
        })
        real_time_data = pd.DataFrame({
            'price': [36000],
            'liquidity': [500000],
            'price_change_1h': [0.02]
        })
        combined_df = combine_data(historical_data, real_time_data)
        print(combined_df)
    """
    if historical_data is None:
        return None

    df = pd.DataFrame(historical_data)
    df["date"] = df["date"].apply(lambda x: datetime.fromtimestamp(x / 1000, pytz.utc).strftime('%Y-%m-%d'))

    df = calculate_indicators(df)

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
