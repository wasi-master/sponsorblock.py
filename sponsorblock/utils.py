import functools
import logging
import os
import platform
import re
from enum import Enum
from datetime import datetime, timedelta
try:
    from typing import Dict, Literal
except ImportError:
    from typing import Dict
    from typing_extensions import Literal

VIDEO_ID_REGEX = re.compile(
    r"(.+?)(\/)(watch\x3Fv=)?(embed\/watch\x3Ffeature\=player_embedded\x26v=)?([a-zA-Z0-9_-]{11})+"
)
ALL_CATEGORIES = [
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "hook",
    "music_offtopic",
    "poi_highlight",
    "filler",
    "exclusive_access",
    "chapter",
]
Category = Literal[
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "hook",
    "music_offtopic",
    "poi_highlight",
    "filler",
    "exclusive_access",
    "chapter",
]
ALL_ACTION_TYPES = [
    "skip",
    "mute",
    "full",
    "poi",
    "chapter",
]
ActionType = Literal[
    "skip",
    "mute",
    "full",
    "poi",
    "chapter",
]
__version__ = "1.0.0"

class UserFeature(Enum):
    """Features that can be granted to a user by a VIP.

    See Also
    --------
    sponsorblock.client.Client.set_user_feature : Should be used with the UserFeature
    """

    CHAPTERS = 0
    DEARROW_TITLE_SUBMITTER = 2


class SortType(Enum):
    """0 for by minutes saved, 1 for by view count, 2 for by total submissions

    See Also
    --------
    sponsorblock.client.Client.get_top_users : Should be used with the SortType
    """

    MINUTES_SAVED = 0
    VIEW_COUNT = 1
    TOTAL_SUBMISSIONS = 2


def set_env_var(key: str, value: str):
    """Sets an environment variable to the given value.

    Parameters
    ----------
    key : str
        The key of the environment variable to set.
    value : str
        The value of the environment variable to set.

    Warning
    -------
    Most of the time this shouldn't be used manually, but it's here in case you need to set the SPONSORBLOCK_USER_ID environment variable.
    """
    logging.getLogger(__name__).info("Setting %s environment variable", key)
    operating_system = platform.system()
    if operating_system == "Windows":
        os.system(f'setx {key} "{value}" ')
    elif operating_system in ("Darwin", "Linux"):
        os.system(f'export {key}="{value}" ')


def cache(**kwargs):
    """
    Custom cache implementation taken from https://stackoverflow.com/a/67555155/13123877.

    Parameters
    ----------
    ttl : timedelta, optional
        The time to live for the cache. Defaults to max time supported by the platform.
    max_entries : int
        The maximum number of entries to store in the cache..
    """

    def decorator(function):
        # static function variable for cache, lazy initialization
        try:
            function.cache
        except AttributeError:
            function.cache = {}

        def freeze(value):
            # lists are common arguments (e.g. categories) but are not hashable
            return tuple(value) if isinstance(value, list) else value

        @functools.wraps(function)
        def wrapper(*args, **fkwargs):
            cache_key = tuple(freeze(arg) for arg in args) + tuple(
                sorted((key, freeze(value)) for key, value in fkwargs.items())
            )
            # if nothing valid in cache, insert something
            if (
                cache_key not in function.cache
                or datetime.now() > function.cache[cache_key]["expiry"]
            ):
                if "max_entries" in kwargs:
                    max_entries = kwargs["max_entries"]
                    if max_entries is not None and len(function.cache) >= max_entries:
                        now = datetime.now()
                        function.cache = {
                            key: function.cache[key]
                            for key in function.cache.keys()
                            if function.cache[key]["expiry"] > now
                        }
                        # if nothing is expired that is deletable, delete the first
                        if len(function.cache) >= max_entries:
                            del function.cache[next(iter(function.cache))]
                function.cache[cache_key] = {
                    "result": function(*args, **fkwargs),
                    "expiry": datetime.max
                    if "ttl" not in kwargs
                    else datetime.now() + timedelta(seconds=kwargs["ttl"]),
                }

            # answer from cache
            return function.cache[cache_key]["result"]

        return wrapper

    return decorator


class Singleton(type):
    _instances: Dict['Singleton', 'Singleton'] = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
