from llm.adapters.llama import LlamaAdapter
from core.market_data import combine_data
from devtools import debug
from datetime import datetime
import json


LLM = LlamaAdapter(model="llama3", system_prompt="You are a crypto trading assistant.")

def decide_trade(price, sentiment):
    prompt = f"""
    Market Price: ${price}
    Sentiment Score: {sentiment}

    Should we BUY, SELL, or HOLD?
    """

    response = LLM.completions(prompt)

    return response


def analyze_with_llm(token, chain, pair_address, data):
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
    - Volatility: {data["price_change_1h"].tolist()}
    - 1-hour price change: ${last_row["price_change_1h"]}%

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
        "reasoning": {{
            "type": "string",
            "description": "Reasoning behind the trading decision.",
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
        "insight": {{
            "type": "string",
            "description": "Additional insights or comments on the market trend.",
            "required": true
        }}
    }}

    Always respond with a JSON object by using the above JSON schema. Do not add any additional comments or text outside the JSON structure.
    """

    response = LLM.completions(prompt)

    return json.loads(response)

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
