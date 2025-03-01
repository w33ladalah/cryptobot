from config.settings import config
from web3 import Web3
from web3.eth import Contract
import time

class EthereumExecutor:

    def __init__(self, token_address, network, provider) -> None:
        self.token_address = token_address
        self.network = network
        self.provider = provider

    def execute(self, decision):
        """Execute a trade on Ethereum using web3 (via Infura or Moralis)."""
        web3, my_address, uniswap_router = self._setup_web3_and_uniswap()

        if "BUY" in decision.upper():
            self._execute_buy(web3, my_address, uniswap_router)
        elif "SELL" in decision.upper():
            self._execute_sell(web3, my_address, uniswap_router)
        else:
            print("No valid Ethereum trade decision provided.")

    def _setup_web3_and_uniswap(self):
        """Set up web3 and Uniswap router contract."""
        rpc_url = self._get_rpc_url()
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if not web3.is_connected():
            raise Exception("Unable to connect to Ethereum via the chosen provider.")

        my_address = web3.to_checksum_address(config.WALLET_ADDRESS)
        uniswap_router_address = web3.to_checksum_address("0x7a250d5630b4cf539739df2c5dAcb4c659F2488D")
        uniswap_router_abi = []  # Supply actual ABI
        uniswap_router = web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

        return web3, my_address, uniswap_router

    def _get_rpc_url(self):
        """Get the RPC URL based on provider and network."""
        if self.provider.lower() == "infura":
            return config.INFURA_URL_MAINNET if self.network == "mainnet" else config.INFURA_URL_TESTNET
        elif self.provider.lower() == "moralis":
            return config.MORALIS_URL_MAINNET if self.network == "mainnet" else config.MORALIS_URL_TESTNET
        else:
            raise Exception("Unsupported Ethereum provider.")

    def _execute_buy(self, web3: Web3, my_address, uniswap_router: Contract):
        """Execute a BUY order on Ethereum."""
        print("Executing BUY order on Ethereum...")
        amount_eth = 0.01  # Example: spend 0.01 ETH
        amount_wei = web3.to_wei(amount_eth, 'ether')
        deadline = int(time.time()) + 60
        WETH_ADDRESS = web3.to_checksum_address("0xC02aaa39b223FE8D0A0e5C4F27ead9083C756Cc2")
        path = [WETH_ADDRESS, web3.to_checksum_address(self.token_address)]
        txn = uniswap_router.functions.swapExactETHForTokens(
            0, path, my_address, deadline
        ).build_transaction({
            'from': my_address,
            'value': amount_wei,
            'gas': 200000,
            'gasPrice': web3.to_wei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(my_address)
        })
        signed_tx = web3.eth.account.sign_transaction(txn, config.ETH_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("Ethereum BUY trade executed. TX hash:", web3.to_hex(tx_hash))

    def _execute_sell(self, web3: Web3, my_address, uniswap_router: Contract):
        """Execute a SELL order on Ethereum."""
        print("Executing SELL order on Ethereum...")
        token_address_cs = web3.to_checksum_address(self.token_address)
        erc20 = web3.eth.contract(address=token_address_cs, abi=config.ERC20_ABI)
        amount_tokens = web3.to_wei(1, 'ether')
        current_allowance = erc20.functions.allowance(my_address, uniswap_router.address).call()

        if current_allowance < amount_tokens:
            self._approve_token_spending(web3, my_address, erc20, uniswap_router.address, amount_tokens)

        deadline = int(time.time()) + 60
        path = [token_address_cs, web3.to_checksum_address("0xC02aaa39b223FE8D0A0e5C4F27ead9083C756Cc2")]
        txn = uniswap_router.functions.swapExactTokensForETH(
            amount_tokens, 0, path, my_address, deadline
        ).build_transaction({
            'from': my_address,
            'gas': 300000,
            'gasPrice': web3.to_wei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(my_address)
        })
        signed_tx = web3.eth.account.sign_transaction(txn, config.ETH_PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("Ethereum SELL trade executed. TX hash:", web3.to_hex(tx_hash))

    def _approve_token_spending(self, web3: Web3, my_address, erc20: Contract, uniswap_router_address, amount_tokens):
        """Approve token spending for Uniswap router."""
        print("Approving token spending for Uniswap router...")
        approve_txn = erc20.functions.approve(
            uniswap_router_address, amount_tokens
        ).build_transaction({
            'from': my_address,
            'gas': 60000,
            'gasPrice': web3.to_wei('5', 'gwei'),
            'nonce': web3.eth.get_transaction_count(my_address)
        })
        signed_approve = web3.eth.account.sign_transaction(approve_txn, config.ETH_PRIVATE_KEY)
        approve_tx_hash = web3.eth.send_raw_transaction(signed_approve.raw_transaction)
        print("Approval TX hash:", web3.to_hex(approve_tx_hash))
        web3.eth.wait_for_transaction_receipt(approve_tx_hash)
