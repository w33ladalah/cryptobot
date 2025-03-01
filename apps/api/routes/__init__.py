from routes.token_pair import routers as TokenPairRouters
from routes.token import router as TokenRouters
from routes.platform import router as PlatformRouters
from routes.data_source import router as DataSourceRouters
from routes.analysis import routers as AnalysisRouters
from routes.user import router as UserRouters

__all__ = [
    'TokenPairRouters',
    'TokenRouters',
    'PlatformRouters',
    'DataSourceRouters',
    'AnalysisRouters',
    'UserRouters',
]
