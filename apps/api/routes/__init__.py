from routes.token_pair import routers as TokenPairRouters
from routes.token import router as TokenRouters
from routes.platform import router as PlatformRouters

__all__ = [
    'TokenPairRouters',
    'TokenRouters',
    'PlatformRouters',
]
