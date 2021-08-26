import os
import platform
import re
from enum import Enum
from typing import Literal

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
    "music_offtopic",
    "poi_highlight",
]
Category = Literal[
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "music_offtopic",
    "poi_highlight",
]


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
    operating_system = platform.system()
    if operating_system == "Windows":
        os.system(f'setx {key} "{value}" ')
    elif operating_system in ("Darwin", "Linux"):
        os.system(f'export {key}="{value}" ')
