"""
Author: Hendro Wibowo
Date: 2025-01-08
"""

from core.market_data import get_historical_data, get_dexscreener_data, combine_data
from llm.llm_analysis import analyze_with_llm
from devtools import debug

def main():
    token_id = "ethereum"
    chain = "ethereum"
    pair_address = "0x2b0ee16991a1a9638fefe4b6d7df1da9a38cbc78"

    # Fetch data
    historical_data = get_historical_data(token_id, days=30)
    real_time_data = get_dexscreener_data(chain, pair_address)

    # Process data
    combined_data = combine_data(historical_data, real_time_data)

    # LLM-based analysis
    analysis_result = analyze_with_llm(token_id, chain, pair_address, combined_data)

    # Display result
    print("Market Analysis:")
    debug(analysis_result)

if __name__ == "__main__":
    main()
