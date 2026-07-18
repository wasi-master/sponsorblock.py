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
from .models import (
    LockReason,
    LockedCategories,
    SearchedUser,
    Segment,
    SegmentInfo,
    SegmentSearchResults,
    ServerStatus,
    TopUser,
    TotalStats,
    User,
    UserStats,
)
from .utils import SortType, UserFeature

__name__ = "sponsorblock.py"  # noqa
__version__ = "0.2.3"
