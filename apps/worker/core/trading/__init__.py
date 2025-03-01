import importlib
from typing import Optional


class TradingExecutor:
    client: Optional[object] = None
    client_class: Optional[str] = None
    token_address: Optional[str] = None
    network: str = "mainnet"

    def __init__(self, token_address, client_class_name, network = 'mainnet', provider = 'infura') -> None:
        self.client_class = client_class_name
        self.token_address = token_address
        self.network = network
        self.provider = provider

        self.load_client_class()

    def load_client_class(self) -> None:
        if not self.client_class:
            raise ValueError("client_class must be set before loading the client class.")

        module_name = f'core.trading.{self.client_class.lower().replace("adapter", "")}'
        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, self.client_class)
            self.client = class_(token_address=self.token_address,
                                 network=self.network,
                                 provider=self.provider)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Error loading client class '{self.client_class}' from module '{module_name}': {e}")

    def get_client(self) -> Optional[object]:
        """Returns the client instance."""
        return self.client

    def execute(self, decision: str) -> None:
        """Executes a decision using the client."""
        if not self.client:
            raise ValueError("Client is not initialized.")
        self.client.execute(decision)
