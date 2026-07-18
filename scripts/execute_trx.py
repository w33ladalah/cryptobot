from core.trading.ethereum import EthereumExecutor

executor = EthereumExecutor(
    token_address="0xbe72e441bf55620febc26715db68d3494213d8cb",  # USDC (test) on Sepolia
    network="testnet",
    provider="infura",
)
executor.execute("BUY", amount_eth=0.001)
