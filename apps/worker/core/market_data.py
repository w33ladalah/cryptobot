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


def get_platforms() -> List[Dict[str, str]]:
    try:
        response = httpx.get(f"{config.COINGECKO_API}/coins/list?include_platform=true")
        response.raise_for_status()
        data = response.json()
        return [{"name": item["name"], "address": item["platforms"]["ethereum"]} for item in data]
    except Exception as e:
        raise Exception(str(e))

def get_dexscreener_data(chain: str, pair_address: str) -> Optional[Dict[str, float]]:
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

    url = f"{config.DEXSCREENER_API}/{chain}/{pair_address}"
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


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators on a price DataFrame.

    Calculates several technical indicators from a pandas DataFrame,
    including Simple Moving Average (SMA), Exponential Moving Average (EMA),
    and volatility metrics. This function returns a modified DataFrame with
    the calculated columns added to it.

    Args:
        df (pd.DataFrame): The input DataFrame containing price data.

    Returns:
        pd.DataFrame: A DataFrame with additional technical indicators added,
        such as 'SMA_14', 'EMA_14', and 'Volatility'.
    """

    df["SMA_14"] = df["price"].rolling(window=14).mean()
    df["EMA_14"] = df["price"].ewm(span=14, adjust=False).mean()
    df["Volatility"] = df["price"].pct_change().rolling(14).std()

    return df


def combine_data(historical_data: Optional[pd.DataFrame], real_time_data: Optional[pd.DataFrame]):
    """
    Merges two datasets based on their indices.

    Args:
        historical_data (pd.DataFrame, optional): Historical data.
        real_time_data (pd.DataFrame, optional): Real-time data. Defaults to None.

    Returns:
        pd.DataFrame: A merged DataFrame with both datasets.

    Note:
        If `real_time_data` is None, the function returns a DataFrame containing only the
        historical data.

    Example:
        >>> df = pd.DataFrame({
            'date': ['2023-10-01', '2023-10-02'],
            'value': [100, 150]
        })
        >>> df_real_time = pd.DataFrame({
            'timestamp': ['14:00', '16:00'],
            'price': [80, 120]
        })
        >>> merged_df = combine_data(df, df_real_time)
        >>> print(merged_df)

        date      value     timestamp    price
        2023-10-01  100       14:00         80
        2023-10-02  150       16:00         120
    """

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
