"""A wrapper for the sponsorblock API."""
from .client import Client
from .errors import (
    BadRequest,
    DuplicateException,
    Forbidden,
    HTTPException,
    InvalidJSONException,
    NotFoundException,
    RateLimitException,
    ServerException,
    UnexpectedException,
)
from .models import Segment, User
from .utils import SortType

__name__ = "sponsorblock.py"  # noqa
__version__ = "0.1.0"
