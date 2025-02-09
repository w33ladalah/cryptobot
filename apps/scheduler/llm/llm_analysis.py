from llm.adapters import LlmAdapter
from core.market_data import combine_data
from config.settings import config
from devtools import debug
from datetime import datetime
import json
import pandas as pd
import traceback


LLM = LlmAdapter()

def decide_trade(price, sentiment):
    prompt = f"""
    Market Price: ${price}
    Sentiment Score: {sentiment}

    Should we BUY, SELL, or HOLD?
    """

    response = LLM.completions(prompt)

    return response


def analyze_with_llm(token: str, chain: str, pair_address: str, data: pd.DataFrame):
    """
    Use LLM to analyze crypto market trends based on structured data.
    :param data: Pandas DataFrame with market data.
    :return: LLM-generated insights and trading decision.
    """
    last_row = data.iloc[-1]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create a structured prompt
    prompt = f"""
    You are a crypto market analyst. Given the following data:

    - Token: {token}
    - Chain: {chain}
    - Pair Address: {pair_address}
    - Date: {timestamp}
    - Current price: ${last_row["price"]}
    - Last recorded price: ${last_row["price_now"]}
    - Historical price trend (last 30 days): {data["price"].tolist()}
    - Liquidity: ${last_row["liquidity"]}
    - 1-hour price change: ${last_row["price_change_1h"]}%
    - SMA: {last_row['SMA_14']}
    - EMA: {last_row['EMA_14']}
    - Volatility: {last_row['Volatility']}

    Analyze the market trend and suggest whether to BUY, SELL, or HOLD.
    Provide reasoning based on historical trends, liquidity, and recent volatility.

    ## The following JSON schema should be used exclusively in your response: ##

    {{
        "token": {{
            "type": "string",
            "description": "The token being analyzed.",
            "required": true
        }},
        "chain": {{
            "type": "string",
            "description": "The blockchain network.",
            "required": true
        }},
        "pair_address": {{
            "type": "string",
            "description": "The pair address for the token.",
            "required": true
        }},
        "date": {{
            "type": "string",
            "description": "The current date.",
            "required": true
        }},
        "decision": {{
            "type": "string",
            "description": "The trading decision based on the analysis (BUY, SELL, or HOLD).",
            "required": true
        }},
        "trend": {{
            "type": "string",
            "description": "The predicted market trend (e.g., bullish, bearish).",
            "required": true
        }},
        "sentiment":  {{
            "type":  "string",
            "description":  "The sentiment score for the token.",
            "required": true
        }},
        "volatility":  {{
            "type":  "string",
            "description":   "The volatility score for the token.",
            "required": true
        }},
        "reasoning": {{
            "type": "string",
            "description": "Reasoning behind the trading decision.",
            "required": true
        }},
        "insight": {{
            "type": "string",
            "description": "Additional insights or comments on the market trend.",
            "required": true
        }}
    }}

    Always respond with a JSON object by using the above JSON schema. Do not add any additional comments or text outside the JSON structure.
    """
    try:
        response = LLM.completions(prompt)

        return json.loads(response)
    except Exception as e:
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Sample data for testing
    import pandas as pd

    historical_data = [
        {"date": 1626220800000, "price": 3200},
        {"date": 1626307200000, "price": 3300},
        {"date": 1626393600000, "price": 3400},
        {"date": 1626480000000, "price": 3500},
        {"date": 1626566400000, "price": 3600},
    ]

    real_time_data = {
        "price": 3700,
        "liquidity": 1000000,
        "price_change_1h": 2.5
    }

    data = combine_data(historical_data, real_time_data)
    print(analyze_with_llm(data))
    print(decide_trade(price=3700, sentiment=0.8))
