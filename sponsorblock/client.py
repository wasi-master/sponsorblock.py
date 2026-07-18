"""Module for the client class."""
import json
import os
import secrets
from datetime import timedelta
from hashlib import sha256
from typing import List, Union

import requests

from .errors import (
    BadRequest,
    DuplicateException,
    Forbidden,
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
    ServerStatus,
    Segment,
    SegmentInfo,
    SegmentSearchResults,
    TopUser,
    TotalStats,
    User,
    UserStats,
)
from .utils import (
    ALL_CATEGORIES,
    VIDEO_ID_REGEX,
    ActionType,
    Category,
    SortType,
    UserFeature,
    set_env_var,
    cache,
    Singleton,
    __version__,
)


def raise_request_exception(response: requests.Response):
    """
    If the server returns a status code, which is not 200,
    it needs to raise an exception:

    Every exception inherits from HTTPException

    :param response:
    :return:
    """
    code = response.status_code

    if code == 200:
        return

    if code == 400:
        raise BadRequest("Your inputs are wrong/impossible", response)

    if code == 403:
        raise Forbidden("Rejected by auto moderator", response)

    if code == 429:
        raise RateLimitException("Rate Limit (Too many for the same user or IP)", response)

    if code == 409:
        raise DuplicateException("Duplicate", response)

    if code == 404:
        raise NotFoundException("Not Found", response)

    if code >= 500:
        raise ServerException("Server Error", response)

    raise UnexpectedException(
        "Unexpected response from server", response
    )


class Client(metaclass=Singleton):
    """A client for making requests to the sponsorblock server."""

    def __init__(
        self,
        user_id=None,
        *,
        base_url: str = None,
        debug: bool = False,
        no_env: bool = False,
        default_categories: List[str] = None,
        hashed_video_id_length: int = 4,
        session: requests.Session = None,
    ):

        """A client for making requests to the sponsorblock server.

        Parameters
        ----------
        user_id : str, optional
            The user id to use for authentication, if not provided, generates a new random one and uses that instead
        base_url : str, optional
            The url to send the requests to, by default https://sponsor.ajay.app
        debug : bool, optional
            Whether to log debug information, by default False
        no_env : bool, optional
            Whether to not store the current user_id in a environment variable, by default False
        default_categories : List[str], optional
            The default categories to use, by default [sponsor, selfpromo, interaction, intro, outro, preview, music_offtopic]
        hashed_video_id_length : int, optional
            The length of the hashed video id to use for K-Anonymity, by default 4
        session : requests.Session, optional
            The session to use for requests, by default a new session

        Warning
        -------
        Passing an user_id would automatically store it in a environment variable to use later. to not have this behavior, you should specify no_env=True
        If you want to change that environment variable later use ``sponsorblock.utils.set_env_var("SPONSORBLOCK_USER_ID", "your_user_id")``

        See Also
        --------
        sponsorblock.utils.set_env_var : Use this to change the environment variable for the user id
        """
        self.base_url = base_url or "https://sponsor.ajay.app"
        if not no_env and os.environ.get("SPONSORBLOCK_USER_ID"):
            self.user_id = user_id or os.environ["SPONSORBLOCK_USER_ID"]
        else:
            self.user_id = user_id or secrets.token_hex(32)
            if not no_env:
                set_env_var("SPONSORBLOCK_USER_ID", self.user_id)
        self.debug = debug
        self.default_categories = default_categories or ALL_CATEGORIES
        self.hash_length = hashed_video_id_length
        self.session = session or requests.Session()

    @cache(ttl=300)  # 5 minutes
    def get_skip_segments(
        self,
        video_id: str,
        *,
        category: Category = None,
        categories: List[str] = None,
        required_segments: List[str] = None,
        action_type: ActionType = None,
        action_types: List[str] = None,
        service: str = "YouTube",
    ) -> List[Segment]:
        """Gets the skip segments for a given video.

        Parameters
        ----------
        video_id : str
            The id of the video to get the skip segments for, can be a video url too.
        category : str
            A category to get skip segments for. See https://wiki.sponsor.ajay.app/w/Types
        categories : List[str]
            A list of categories to get the skip segments for. See https://wiki.sponsor.ajay.app/w/Types
        required_segments : List[str]
            A list of segment UUIDs to require be retrieved, even if they don't meet the minimum vote threshold.
        action_type : str
            An action type to get segments for (e.g. ``skip``, ``mute``, ``full``, ``poi``, ``chapter``), defaults to ``skip`` on the server. See https://wiki.sponsor.ajay.app/w/Types
        action_types : List[str]
            A list of action types to get segments for. See https://wiki.sponsor.ajay.app/w/Types
        service : str
            The service to use, default is 'YouTube'. See https://wiki.sponsor.ajay.app/w/Types#service.

        Returns
        -------
        List[Segment]
            A list of segments of the video

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because the video id is invalid
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> segments = client.get_skip_segments("https://www.youtube.com/watch?v=kJQP7kiw5Fk")
        >>> segments
        [
            Segment(category=music_offtopic, start=0, end=21.808434, uuid=728cbf1743f4b5230ee4a9c7b254e316aa90720ec35297b17aaf6d23907c1a83, duration=0:00:21.808434, action_type=skip),
            Segment(category=music_offtopic, start=249.6543, end=281.521, uuid=ae38abe70c63b093eaeb1c2c437aa3275856646c326ee23b5ff70dcb4190c92f, duration=0:00:31.866700, action_type=skip),
            Segment(category=outro, start=274.674, end=281.521, uuid=cd335e7f406df63e460b4b02db71cc57344529d381bb9fc482960f338ff4ae37, duration=0:00:06.847000, action_type=skip),
            Segment(category=poi_highlight, start=27.949, end=27.949, uuid=5e560eec60e99a8f0a5056816800c32bb8c86ff06d4b57cece8f7be5504a1077e, duration=0:00:00, action_type=skip)
        ]
        >>> segments[0].category
        'music_offtopic'
        >>> segments[1].start, segments[1].end
        (249.6543, 281.521)
        >>> segments[2].duration.seconds
        6
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if category:
            categories = [category]
        if action_type:
            action_types = [action_type]
        parameters = {
            "category": categories or self.default_categories,
            "requiredSegment": required_segments or [],
            "service": service,
            "videoID": video_id,
        }
        if action_types:
            parameters["actionType"] = action_types
        url = self.base_url + "/api/skipSegments/"
        response = self.session.get(url, params=parameters)
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [Segment.from_dict(d) for d in data]
        finally:
            raise_request_exception(response)

    @cache(ttl=300)  # 5 minutes
    def get_skip_segments_with_hash(
        self,
        video_id: str ,
        video_hash: str = None,
        *,
        category: Category = None,
        categories: List[str] = None,
        required_segments: List[str] = None,
        action_type: ActionType = None,
        action_types: List[str] = None,
        service: str = "YouTube",
    ) -> List[Segment]:
        """
        Gets the skip segments for a given video using a K-Anonymity system.

        Parameters
        ----------
        video_id : str
            The id of the video to get the skip segments for, can be a video url too.
        video_hash : str
            The sha256 hash of the id of the video to get the skip segments for, if not given uses video_id to generate a hash with the length 32.
            The video ids are hashed to implement a K-Anonymity system (https://github.com/ajayyy/SponsorBlock/wiki/K-Anonymity).
            The length can be from 4 (recommended) to 32. A higher value would mean faster response times, but it's just a few nanoseconds
        category : str
            A category to get skip segments for. See https://wiki.sponsor.ajay.app/w/Types
        categories : List[str]
            A list of categories to get the skip segments for. See https://wiki.sponsor.ajay.app/w/Types
        required_segments : List[str]
            A list of segment UUIDs to require be retrieved, even if they don't meet the minimum vote threshold.
        action_type : str
            An action type to get segments for (e.g. ``skip``, ``mute``, ``full``, ``poi``, ``chapter``), defaults to ``skip`` on the server. See https://wiki.sponsor.ajay.app/w/Types
        action_types : List[str]
            A list of action types to get segments for. See https://wiki.sponsor.ajay.app/w/Types
        service : str
            The service to use, default is 'YouTube'. See https://wiki.sponsor.ajay.app/w/Types#service.


        Returns
        -------
        List[Segment]
            A list of segments of the video

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because the video id is invalid
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> segments = client.get_skip_segments_with_hash("f1d9e193c3a58e59468eb88b50929d80")
        >>> segments
        [
            Segment(category=music_offtopic, start=0, end=21.808434, uuid=728cbf1743f4b5230ee4a9c7b254e316aa90720ec35297b17aaf6d23907c1a83, duration=0:00:21.808434, action_type=skip),
            Segment(category=music_offtopic, start=249.49852, end=281.521, uuid=3d78f759477445f70f04063df12523038eff3928c6a99c11e7cdd3bd9a51311f, duration=0:00:32.022480, action_type=skip),
            Segment(category=outro, start=274.674, end=281.521, uuid=cd335e7f406df63e460b4b02db71cc57344529d381bb9fc482960f338ff4ae37, duration=0:00:06.847000, action_type=skip),
            Segment(category=poi_highlight, start=27.949, end=27.949, uuid=5e560eec60e99a8f0a5056816800c32bb8c86ff06d4b57cece8f7be5504a1077e, duration=0:00:00, action_type=skip)
        ]
        >>> segments[0].category
        'music_offtopic'
        >>> segments[1].start, segments[1].end
        (249.6543, 281.521)
        >>> segments[2].duration.seconds
        6
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if video_hash and not 4 <= len(video_hash) <= 32:
            raise TypeError(
                "Video hash length wrong. must be between 4 and 32, got {}".format(
                    len(video_hash)
                )
            )
        if category:
            categories = [category]
        if action_type:
            action_types = [action_type]
        parameters = {
            "category": categories or self.default_categories,
            "requiredSegment": required_segments or [],
            "service": service,
        }
        if action_types:
            parameters["actionType"] = action_types
        url = self.base_url + "/api/skipSegments/" + (
            video_hash or sha256(video_id.encode("utf-8")).hexdigest()[: self.hash_length]
        )
        response = self.session.get(url, params=parameters)
        try:
            data = json.loads(response.text)
            for video in data:
                if video["videoID"] == video_id:
                    data = video["segments"]
                    break
            else:
                raise BadRequest(
                    "No video returned from server with the specified hash", response
                )
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [Segment.from_dict(d) for d in data]
        finally:
            raise_request_exception(response)

    def add_skip_segments(
        self,
        video_id: str,
        *,
        segment: Segment = None,
        segments: List[Segment] = None,
        service: str = "YouTube",
    ) -> None:
        """Add a skip segment to the server.

        Parameters
        ----------
        video_id : str
            The id of the video to add the skip segment to, can be a video url too.
        segment : Segment
            The skip segment to add
        segments : List[Segment]
            The list of skip segments to add
        service : str
            The service to use, default is 'YouTube'. See https://wiki.sponsor.ajay.app/w/Types#service.

        Raises
        ------
        ValueError
            No segments were specified
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not allowed to add skip segments
        RateLimitException
            The server returned a 429 error, most likely because you are making too many requests
        DuplicateException
            The server returned a 409 error, most likely because the skip segment already exists
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled

        Examples
        --------
        >>> \"\"\"Adding new segments to a YouTube video (Note: this is a example and don't try this yourself)\"\"\"
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.add_skip_segments(
                "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
                segment=sb.Segment(category="music_offtopic", start=0, end=21.808434, action_type="skip")
            )
        """
        if segment is None and not segments:
            raise ValueError("At least one segment is required")
        segments = segments or []
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if segment:
            segments.extend([segment])

        body = {
            "videoID": video_id,
            "userID": self.user_id,
            "userAgent": f"{__name__}/{__version__}",
            "service": service,
            "segments": [
                {
                    "segment": [
                        s.total_seconds() if isinstance(s, timedelta) else s
                        for s in [segment.start, segment.end]
                    ],
                    "category": segment.category,
                    "actionType": segment.action_type or "skip",
                    "description": segment.description or "",
                }
                for segment in segments
            ],
        }
        url = self.base_url + "/api/skipSegments"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def vote_skip_segment(
        self,
        uuid: Union[Segment, str],
        *,
        vote: Union[str, int, bool] = None,
        category: Category = None,
    ) -> None:
        """Votes on a skip segment.

        Parameters
        ----------
        uuid : Union[Segment, str]
            segment or uuid of the segment being voted on
        vote : Union[str, int, bool], optional
            The vote to vote on the skip segment.
            Can be any of ``yes``, ``upvote``, ``up``, ``good``, ``1``, ``True`` for upvoting,
            ``no``, ``downvote``, ``down``, ``bad``, ``0``, ``False`` for downvoting,
            and ``undo`` for undoing a given vote
        category : Category, optional
            The category of the skip segment. This can be used as an alternative to the vote parameter, by default None

        Raises
        ------
        ValueError
            You passed both vote and category.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not allowed to vote on the skip segment
        ServerException
            The server returned a error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 403, 429, 409, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> segments = client.get_skip_segments("https://www.youtube.com/watch?v=kJQP7kiw5Fk")
        >>> client.vote_skip_segment(segments[0], 'yes')
        """

        if category is None and vote is None:
            raise ValueError("At least one argument is required")
        if category is not None and vote is not None:
            raise ValueError("Only one of vote and category can be passed")

        if vote is not None:
            if vote in ("yes", "upvote", "up", "good", 1, "1", True, "True"):
                vote = 1
            elif vote in ("no", "downvote", "down", "bad", 0, "0", False, "False"):
                vote = 0
            elif vote in ("undo", 20):
                vote = 20
            else:
                vote = int(bool(vote))

        parameters = {
            "UUID": uuid.uuid if isinstance(uuid, Segment) else uuid,
            "userID": self.user_id,
        }

        if vote is not None:
            parameters["type"] = vote
        if category is not None:
            parameters["category"] = category

        url = self.base_url + "/api/voteOnSponsorTime"
        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    def post_viewed_video_sponsor_time(self, uuid: Union[Segment, str]):
        """Notifies the server that a segment has been skipped.

        Parameters
        ----------
        uuid : Union[Segment, str]
            The uuid of the segment that was skipped

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> segments = client.get_skip_segments("https://www.youtube.com/watch?v=kJQP7kiw5Fk")
        >>> client.post_viewed_video_sponsor_time(segments[1])
        """
        parameters = {"UUID": uuid.uuid if isinstance(uuid, Segment) else uuid}
        url = self.base_url + "/api/viewedVideoSponsorTime"

        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    @cache(ttl=900)  # 15 minutes
    def get_user_info(self, public_userid: str = None) -> User:
        """Gets the user info for the current user.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to get information for, by default the current user id.

        Returns
        -------
        User
            The user info for the specified user.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because the user was not found.
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> \"\"\"Example of getting the user info for the current user (a valid user id needs to be passed to the client):\"\"\"
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.get_user_info()
        User(
            user_id=32be414f723dafb3b6903e92e1694f55f104de19c78d5f158c01c38e791fb792,
            user_name=Wasi Master,
            minutes_saved=1261.9740212202073,
            segment_count=47,
            ignored_segment_count=0,
            view_count=4367,
            ignored_view_count=0,
            warnings=0,
            reputation=0.04827586206896552,
            vip=False,
            last_segment_id=314db4f4677bbf6c8f9f614f82ba540fe1e2d596d490b5212a6d72a1b0cf266cb
        )
        >>> \"\"\"Example of getting the user info for a specified user (a valid public user id needs to be passed to the method)\"\"\"
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> user = client.get_user_info("57ddecc5b36813ddb8ea1eba73342c8a783527b884b6ebcb177bf37cafce7620")
        User(
            user_id=57ddecc5b36813ddb8ea1eba73342c8a783527b884b6ebcb177bf37cafce7620,
            user_name=PureFallen,
            minutes_saved=240084.80235477304,
            segment_count=1407,
            ignored_segment_count=16,
            view_count=550885,
            ignored_view_count=3071,
            warnings=0,
            reputation=4.689655172413794,
            vip=True,
            last_segment_id=1490a3d5e4f966ecc745e21f2d23458f4952c84382e7c16e4859ca20c59daa21
        )
        >>> user.user_name
        'PureFallen'
        """
        if public_userid is None:
            params = {"userID": self.user_id}
        else:
            params = {"publicUserID": public_userid}

        url = self.base_url + "/api/userInfo"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return User(data)
        finally:
            raise_request_exception(response)

    @cache(ttl=900)  # 15 minutes
    def get_user_stats(
        self,
        public_userid: str = None,
        *,
        fetch_category_stats: bool = False,
        fetch_action_type_stats: bool = False,
    ) -> UserStats:
        """Gets the stats for a user.

        Parameters
        ----------
        public_userid : str, optional
            The public user id of the user to get stats for, by default the current user id.
        fetch_category_stats : bool, optional
            Whether to also fetch the number of segments per category, by default False
        fetch_action_type_stats : bool, optional
            Whether to also fetch the number of segments per action type, by default False

        Returns
        -------
        UserStats
            The stats for the specified user.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.get_user_stats(fetch_category_stats=True)
        UserStats(
            user_id=32be414f723dafb3b6903e92e1694f55f104de19c78d5f158c01c38e791fb792,
            user_name=Wasi Master,
            minutes_saved=1261,
            segment_count=47,
            category_counts={'sponsor': 20, 'intro': 5, ...},
            action_type_counts=None
        )
        """
        if public_userid is None:
            params = {"userID": self.user_id}
        else:
            params = {"publicUserID": public_userid}
        if fetch_category_stats:
            params["fetchCategoryStats"] = "true"
        if fetch_action_type_stats:
            params["fetchActionTypeStats"] = "true"

        url = self.base_url + "/api/userStats"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return UserStats(data)
        finally:
            raise_request_exception(response)

    @cache(ttl=60)  # a minute
    def get_views_for_user(self):
        """Gets the view count for the current user.

        Returns
        -------
        int
            The amount of views for the current user.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        NotFoundException
            The server returned a 404 error, most likely because the user was not found.
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.views_for_user()
        4367
        """
        params = {"userID": self.user_id}

        url = self.base_url + "/api/getViewsForUser"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return data["viewCount"]
        finally:
            raise_request_exception(response)

    @cache(ttl=60)  # a minute
    def get_saved_time_for_user(self):
        """Gets the view count for the current user.

        Returns
        -------
        int
            The amount of views for the current user in minutes.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        NotFoundException
            The server returned a 404 error, most likely because the user was not found.
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.saved_time_for_user()
        1181.974021220207
        """
        params = {"userID": self.user_id}

        url = self.base_url + "/api/getSavedTimeForUser"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return data["timeSaved"]
        finally:
            raise_request_exception(response)

    def set_user_name(self, user_name: str):
        """Sets the user name for the current user.

        Parameters
        ----------
        user_name : str
            The user name to set for the current user.

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.set_user_name("NoobMaster69")
        """
        parameters = {
            "userID": self.user_id,
            "username": user_name,
        }

        url = self.base_url + "/api/setUsername"
        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    @cache(ttl=60)  # a minute
    def get_user_name(self) -> str:
        """Gets the user name for the current user.

        Returns
        -------
        str
            The user name for the current user.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because the user was not found.
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.get_user_name()
        'NoobMaster69'
        """

        params = {"userID": self.user_id}
        url = self.base_url + "/api/getUsername"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return data["userName"]
        finally:
            raise_request_exception(response)

    @cache(ttl=3600)  # a minute
    def get_top_users(self, sort_type: SortType) -> List[TopUser]:
        """Gets the top users.

        Paremeters
        ----------
        sort_type : SortType
            The sort type, can be either `SortType.MINUTES_SAVED`, `SortType.VIEW_COUNT`, or `SortType.TOTAL_SUBMISSIONS`

        Returns
        -------
        List[TopUser]
            The list of top 100 users.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> from sponsorblock import SortType
        >>> client = sb.Client()
        >>> top_users = client.get_top_users(sort_type=SortType.VIEW_COUNT)  # or `SortType.MINUTES_SAVED` or `SortType.TOTAL_SUBMISSIONS`
        >>> top_users
        [
            TopUser(user_name=cane, view_count=9663381, total_submissions=4773, minutes_saved=3061714.88099481),
            TopUser(user_name=FunkeymonkeyTTR, view_count=5061381, total_submissions=11604, minutes_saved=1312617.9428691764),
            TopUser(user_name=ltcars, view_count=4997845, total_submissions=4315, minutes_saved=1520388.8714212843),
            TopUser(user_name=GrandMaesterJ, view_count=2157448, total_submissions=3934, minutes_saved=758912.7349532802),
            TopUser(user_name=Zenomit, view_count=1588073, total_submissions=4026, minutes_saved=478283.88908721233),
            TopUser(user_name=E.Coli, view_count=1558146, total_submissions=6100, minutes_saved=412567.07062993734),
            ... # and so on (100 users)
        ]
        >>> top_users[0].user_name
        'cane'
        >>> top_users[2].view_count
        4997845
        """

        params = {
            "sortType": sort_type.value
            if isinstance(sort_type, SortType)
            else sort_type
        }
        url = self.base_url + "/api/getTopUsers"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [
                TopUser(user_name, view_count, total_submissions, minutes_saved)
                for user_name, view_count, total_submissions, minutes_saved in zip(
                    data["userNames"],
                    data["viewCounts"],
                    data["totalSubmissions"],
                    data["minutesSaved"],
                )
            ]
        finally:
            raise_request_exception(response)

    @cache(ttl=60)  # a minute
    def get_total_stats(self, count_contributing_users: bool = False) -> TotalStats:
        """Gets total stats for the api

        Parameters
        ----------
        count_contributing_users : bool
            Whether or not to count the number of users who have contributed to the api.

        Returns
        -------
        TotalStats
            The total stats for the api.

        Raises
        ------
        InvalidJSONException
            The server returned a response that was not valid JSON.
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> totalstats = client.get_total_stats()
        >>> totalstats
        TotalStats(
            user_count=170551,
            active_users=295571,
            api_users=1323906,
            view_count=286114842,
            total_submissions=1946245,
            minutes_saved=144998543.20013103
        )
        >>> totalstats.user_count
        170551
        """
        parameters = {"countContributingUsers": count_contributing_users}
        url = self.base_url + "/api/getTotalStats"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return TotalStats(data)
        finally:
            raise_request_exception(response)

    @cache(ttl=60)  # a minute
    def get_saved_days_formatted(self) -> float:
        """Returns the amount of days that have been saved.

        Returns
        -------
        float
            The amount of days that have been saved

        Raises
        ------
        InvalidJSONException
            The server returned invalid JSON
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.get_saved_days_formatted()
        132654.20
        """
        url = self.base_url + "/api/getDaysSavedFormatted"
        response = self.session.get(url)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return float(data["daysSaved"])
        finally:
            raise_request_exception(response)

    @cache(max_entries=300)  # 5 minutes
    def get_segment_info(
        self,
        segment: Union[Segment, str] = None,
        segments: List[Union[Segment, str]] = None,
    ) -> List[SegmentInfo]:
        """Gets detailed information about a segment.

        Parameters
        ----------
        segment : Union[Segment, str], optional
            The segment to get information about., by default None
        segments : List[Union[Segment, str]], optional
            A list of segments to get information about, by default None

        Returns
        -------
        List[SegmentInfo]
            The information about the segment(s) specified.

        Raises
        ------
        ValueError
            No segment were specified.
        InvalidJSONException
            The server returned invalid JSON.
        ServerException
            The server returned a 500 error, most likely because the server is unavailable.
        NotFoundException
            The segment(s) specified were not found.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible or exceeds the maximum allowed size.
        UnexpectedException
            The server returned a response that was not 200, 400, or 500.

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> segments = client.get_skip_segments("https://www.youtube.com/watch?v=kJQP7kiw5Fk")
        >>> segment_infos = client.get_segment_info(segments=segments)
        >>> segment_infos
        [
            SegmentInfo(
                video_id=kJQP7kiw5Fk,
                start_time=0,
                end_time=21.808434,
                votes=15,
                locked=0,
                uuid=728cbf1743f4b5230ee4a9c7b254e316aa90720ec35297b17aaf6d23907c1a83,
                user_id=2ad8fd8d67e5321fed0e6c1b46682c2db3c4d5734434715712f4d1292ee2781e,
                time_submitted=2020-06-16 20:00:05.037000,
                views=43655,
                category=music_offtopic,
                service=YouTube,
                video_duration=0,
                hashed_video_id=f1d9e193c3a58e59468eb88b50929d8095ccfa2476ed8db58e5907cafc890d9f,
                user_agent=""
            ),
            ... (more segments)
        ]
        >>> segment_infos[0].time_submitted.day
        16
        """
        if segment is None and not segments:
            raise ValueError("At least one segment is required")
        segments = list(segments) if segments else []
        if segment:
            segments.extend([segment])
        parameters = {
            "UUID": [
                segment.uuid if isinstance(segment, Segment) else str(segment)
                for segment in segments
            ]
        }
        url = self.base_url + "/api/segmentInfo"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [SegmentInfo(segment_info) for segment_info in data]
        finally:
            raise_request_exception(response)

    @cache(ttl=300)  # 5 minutes
    def get_locked_categories(
        self, video_id: str, *, action_types: List[str] = None
    ) -> LockedCategories:
        """Gets the locked categories for a video.

        Parameters
        ----------
        video_id : str
            The id of the video to get the locked categories for, can be a video url too.
        action_types : List[str], optional
            The action types to get locks for, defaults to ``["skip", "mute"]`` on the server.

        Returns
        -------
        LockedCategories
            The locked categories for the video, along with the most recent lock reason.

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because the video has no locked categories
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.get_locked_categories("kJQP7kiw5Fk")
        LockedCategories(categories=['music_offtopic'], reason=..., action_types=['skip', 'mute'], video_id=None)
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        parameters = {"videoID": video_id}
        if action_types:
            parameters["actionTypes"] = json.dumps(action_types)
        url = self.base_url + "/api/lockCategories"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return LockedCategories(data)
        finally:
            raise_request_exception(response)

    @cache(ttl=300)  # 5 minutes
    def get_locked_categories_with_hash(
        self, video_id: str, video_hash: str = None
    ) -> LockedCategories:
        """Gets the locked categories for a video using a K-Anonymity system.

        Parameters
        ----------
        video_id : str
            The id of the video to get the locked categories for, can be a video url too.
        video_hash : str, optional
            The sha256 hash prefix of the video id, if not given it is generated from the
            video id using the client's hashed_video_id_length. Must be between 4 and 32 characters.

        Returns
        -------
        LockedCategories
            The locked categories for the video, along with the video id, full hash and lock reason.

        Raises
        ------
        ValueError
            The video id is invalid
        TypeError
            The video hash length is not between 4 and 32
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server did not return a lock for the requested video
        NotFoundException
            The server returned a 404 error, most likely because the video has no locked categories
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.get_locked_categories_with_hash("kJQP7kiw5Fk")
        LockedCategories(categories=['music_offtopic'], reason=..., action_types=None, video_id=kJQP7kiw5Fk)
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if video_hash and not 4 <= len(video_hash) <= 32:
            raise TypeError(
                "Video hash length wrong. must be between 4 and 32, got {}".format(
                    len(video_hash)
                )
            )
        url = self.base_url + "/api/lockCategories/" + (
            video_hash or sha256(video_id.encode("utf-8")).hexdigest()[: self.hash_length]
        )
        response = self.session.get(url)

        try:
            data = json.loads(response.text)
            for video in data:
                if video["videoID"] == video_id:
                    data = video
                    break
            else:
                raise BadRequest(
                    "No lock returned from server with the specified hash", response
                )
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return LockedCategories(data)
        finally:
            raise_request_exception(response)

    @cache(ttl=300)  # 5 minutes
    def get_lock_reason(
        self,
        video_id: str,
        *,
        category: Category = None,
        categories: List[str] = None,
        action_types: List[str] = None,
    ) -> List[LockReason]:
        """Gets the lock reasons for the categories of a video.

        Parameters
        ----------
        video_id : str
            The id of the video to get the lock reasons for, can be a video url too.
        category : str, optional
            A single category to get the lock reason for, defaults to all categories.
        categories : List[str], optional
            The categories to get the lock reasons for, defaults to all categories.
        action_types : List[str], optional
            The action types to get lock reasons for.

        Returns
        -------
        List[LockReason]
            The lock status and reason for each requested category.

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.get_lock_reason("kJQP7kiw5Fk", category="music_offtopic")
        [LockReason(category=music_offtopic, locked=1, reason=..., user_id=..., user_name=...)]
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if category:
            categories = [category]
        parameters = {"videoID": video_id}
        if categories:
            parameters["categories"] = json.dumps(categories)
        if action_types:
            parameters["actionTypes"] = json.dumps(action_types)
        url = self.base_url + "/api/lockReason"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [LockReason(d) for d in data]
        finally:
            raise_request_exception(response)

    def lock_categories(
        self,
        video_id: str,
        categories: List[str],
        *,
        reason: str = "",
        action_types: List[str] = None,
    ) -> None:
        """Locks categories on a video, disallowing further submissions for those categories.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        video_id : str
            The id of the video to lock categories on, can be a video url too.
        categories : List[str]
            The categories to lock.
        reason : str, optional
            The reason for the lock, by default an empty string.
        action_types : List[str], optional
            The action types the lock applies to.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 403, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local vip user id")
        >>> client.lock_categories("kJQP7kiw5Fk", ["sponsor"], reason="Spam submissions")
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        body = {
            "videoID": video_id,
            "userID": self.user_id,
            "categories": categories,
            "reason": reason,
        }
        if action_types:
            body["actionTypes"] = action_types
        url = self.base_url + "/api/lockCategories"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def unlock_categories(self, video_id: str, categories: List[str]) -> None:
        """Removes category locks on a video.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        video_id : str
            The id of the video to unlock categories on, can be a video url too.
        categories : List[str]
            The categories to unlock.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 403, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local vip user id")
        >>> client.unlock_categories("kJQP7kiw5Fk", ["sponsor"])
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        body = {
            "videoID": video_id,
            "userID": self.user_id,
            "categories": categories,
        }
        url = self.base_url + "/api/lockCategories"
        response = self.session.delete(url, json=body)
        raise_request_exception(response)

    @cache(ttl=300)  # 5 minutes
    def search_segments(
        self,
        video_id: str,
        *,
        category: Category = None,
        categories: List[str] = None,
        action_type: ActionType = None,
        action_types: List[str] = None,
        service: str = "YouTube",
        page: int = 0,
        min_votes: int = None,
        max_votes: int = None,
        min_views: int = None,
        max_views: int = None,
        locked: bool = True,
        hidden: bool = True,
        ignored: bool = True,
    ) -> SegmentSearchResults:
        """Searches all segments of a video based on the specified filters.

        Note
        ----
        This should not be used to know which segments to skip, since the vote and view
        thresholds that determine the best segments change over time. Use
        :meth:`get_skip_segments` for that.

        Parameters
        ----------
        video_id : str
            The id of the video to search the segments of, can be a video url too.
        category : str, optional
            A category to search segments for. See https://wiki.sponsor.ajay.app/w/Types
        categories : List[str], optional
            A list of categories to search segments for.
        action_type : str, optional
            An action type to search segments for.
        action_types : List[str], optional
            A list of action types to search segments for.
        service : str, optional
            The service to use, default is 'YouTube'.
        page : int, optional
            The page of results to get (10 segments per page), by default 0.
        min_votes : int, optional
            Only return segments with at least this many votes.
        max_votes : int, optional
            Only return segments with at most this many votes.
        min_views : int, optional
            Only return segments with at least this many views.
        max_views : int, optional
            Only return segments with at most this many views.
        locked : bool, optional
            Whether to include locked segments, by default True.
        hidden : bool, optional
            Whether to include hidden segments, by default True.
        ignored : bool, optional
            Whether to include ignored segments (hidden or below the vote threshold), by default True.

        Returns
        -------
        SegmentSearchResults
            The total segment count, the page number, and up to 10 segments.

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        NotFoundException
            The server returned a 404 error, most likely because there are no matching segments
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> results = client.search_segments("kJQP7kiw5Fk", min_votes=0)
        >>> results.segment_count
        16
        >>> results.segments[0].category
        'music_offtopic'
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        if category:
            categories = [category]
        if action_type:
            action_types = [action_type]
        parameters = {
            "videoID": video_id,
            "service": service,
            "page": page,
        }
        if categories:
            parameters["categories"] = json.dumps(categories)
        if action_types:
            parameters["actionTypes"] = json.dumps(action_types)
        if min_votes is not None:
            parameters["minVotes"] = min_votes
        if max_votes is not None:
            parameters["maxVotes"] = max_votes
        if min_views is not None:
            parameters["minViews"] = min_views
        if max_views is not None:
            parameters["maxViews"] = max_views
        if not locked:
            parameters["locked"] = "false"
        if not hidden:
            parameters["hidden"] = "false"
        if not ignored:
            parameters["ignored"] = "false"
        url = self.base_url + "/api/searchSegments"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return SegmentSearchResults(data)
        finally:
            raise_request_exception(response)

    def get_status(self, value: str = None) -> Union[ServerStatus, int, str, list]:
        """Gets the status of the sponsorblock server.

        This includes information about the database, such as the current database version,
        along with uptime, load averages and more.

        Parameters
        ----------
        value : str, optional
            A single status field to get (e.g. ``uptime``, ``db``, ``loadavg``), by default
            all fields are fetched and a ServerStatus is returned.

        Returns
        -------
        Union[ServerStatus, int, str, list]
            The status of the server, or the single requested value.

        Raises
        ------
        InvalidJSONException
            The server returned invalid JSON
        NotFoundException
            The server returned a 404 error, most likely because the requested value does not exist
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 404, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client()
        >>> client.get_status()
        ServerStatus(uptime=244459.26, commit=bfca2fb0..., db=46, ...)
        >>> client.get_status("db")
        46
        """
        url = self.base_url + "/api/status" + (f"/{value}" if value else "")
        response = self.session.get(url)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            if value is not None:
                return data[value] if isinstance(data, dict) else data
            return ServerStatus(data)
        finally:
            raise_request_exception(response)

    def is_user_vip(self) -> bool:
        """Checks whether the current user is a VIP.

        Returns
        -------
        bool
            Whether the current user is a VIP.

        Raises
        ------
        InvalidJSONException
            The server returned invalid JSON
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response that was not 200, 400, or 500

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.is_user_vip()
        False
        """
        params = {"userID": self.user_id}
        url = self.base_url + "/api/isUserVIP"
        response = self.session.get(url, params=params)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return bool(data["vip"])
        finally:
            raise_request_exception(response)

    def shadow_ban_user(
        self,
        public_userid: str,
        *,
        enabled: bool = True,
        unhide_old_submissions: bool = None,
        categories: List[str] = None,
    ) -> None:
        """Shadow bans or unbans a user, hiding all their future submissions from everyone else.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to shadow ban.
        enabled : bool, optional
            True to ban, False to unban, by default True.
        unhide_old_submissions : bool, optional
            Whether all previous submissions should be (un)hidden as well.
        categories : List[str], optional
            The categories to (un)hide, defaults to all categories on the server.

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        DuplicateException
            The server returned a 409 error, because the user is already shadowbanned
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        parameters = {
            "userID": public_userid,
            "adminUserID": self.user_id,
            "enabled": "true" if enabled else "false",
        }
        if unhide_old_submissions is not None:
            parameters["unHideOldSubmissions"] = (
                "true" if unhide_old_submissions else "false"
            )
        if categories:
            parameters["categories"] = json.dumps(categories)
        url = self.base_url + "/api/shadowBanUser"
        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    def warn_user(
        self, public_userid: str, *, reason: str = "", enabled: bool = True
    ) -> None:
        """Warns a user, temporarily banning them and showing them a warning message.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to warn.
        reason : str, optional
            The reason for the warning.
        enabled : bool, optional
            True to warn, False to remove the warning, by default True.

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        DuplicateException
            The server returned a 409 error, because the user is already warned
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        body = {
            "issuerUserID": self.user_id,
            "userID": public_userid,
            "reason": reason,
            "enabled": enabled,
        }
        url = self.base_url + "/api/warnUser"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def clear_cache(self, video_id: str) -> None:
        """Clears the server's redis cache for a video.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        video_id : str
            The id of the video to clear the cache for, can be a video url too.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        body = {"userID": self.user_id, "videoID": video_id}
        url = self.base_url + "/api/clearCache"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def purge_all_segments(self, video_id: str, *, service: str = "YouTube") -> None:
        """Hides all segments on a video without affecting the submitters' reputations.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        video_id : str
            The id of the video to purge the segments of, can be a video url too.
        service : str, optional
            The service of the video, default is 'YouTube'.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        body = {"userID": self.user_id, "videoID": video_id, "service": service}
        url = self.base_url + "/api/purgeAllSegments"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def segment_shift(
        self, video_id: str, start_time: float, end_time: float
    ) -> None:
        """Shifts all segments on a video.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        video_id : str
            The id of the video to shift the segments of, can be a video url too.
        start_time : float
            The start time of the shift.
        end_time : float
            The end time of the shift.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        if len(video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            video_id = video_id_match.group(5)
        body = {
            "videoID": video_id,
            "userID": self.user_id,
            "startTime": start_time,
            "endTime": end_time,
        }
        url = self.base_url + "/api/segmentShift"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def add_user_as_temp_vip(
        self, public_userid: str, channel_video_id: str, *, enabled: bool = True
    ) -> None:
        """Grants a user temporary (24 hour) VIP status on a channel.

        Note
        ----
        This can only be used by VIP users. A user can only be a temporary VIP of one
        channel at a time, the most recent channel takes precedence.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to grant temporary VIP status to.
        channel_video_id : str
            The id of a video of the channel to grant VIP status on, can be a video url too.
        enabled : bool, optional
            True to grant, False to revoke, by default True.

        Raises
        ------
        ValueError
            The video id is invalid
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        NotFoundException
            The server returned a 404 error, because no channel was found for the video id
        DuplicateException
            The server returned a 409 error, because the user is already a permanent VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        if len(channel_video_id) != 11:
            video_id_match = VIDEO_ID_REGEX.match(channel_video_id)
            if not video_id_match:
                raise ValueError("Invalid video id")
            channel_video_id = video_id_match.group(5)
        parameters = {
            "userID": public_userid,
            "adminUserID": self.user_id,
            "channelVideoID": channel_video_id,
            "enabled": "true" if enabled else "false",
        }
        url = self.base_url + "/api/addUserAsTempVIP"
        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    def set_user_feature(
        self,
        public_userid: str,
        feature: Union[UserFeature, int],
        *,
        enabled: bool = True,
    ) -> None:
        """Adds or removes a feature for a user.

        Note
        ----
        This can only be used by VIP users.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to change the features of.
        feature : Union[UserFeature, int]
            The feature to add or remove, can be a UserFeature or the raw feature number.
        enabled : bool, optional
            True to add the feature, False to remove it, by default True.

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because the feature does not exist
        Forbidden
            The server returned a 403 error, most likely because you are not a VIP
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        body = {
            "userID": public_userid,
            "adminUserID": self.user_id,
            "feature": feature.value if isinstance(feature, UserFeature) else feature,
            "enabled": enabled,
        }
        url = self.base_url + "/api/feature"
        response = self.session.post(url, json=body)
        raise_request_exception(response)

    def add_user_as_vip(self, public_userid: str, *, enabled: bool = True) -> None:
        """Adds or removes a user from the VIP list.

        Note
        ----
        This can only be used by the server administrator.

        Parameters
        ----------
        public_userid : str
            The public user id of the user to add to the VIP list.
        enabled : bool, optional
            True to add the user, False to remove them, by default True.

        Raises
        ------
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible
        Forbidden
            The server returned a 403 error, most likely because you are not the administrator
        ServerException
            The server returned a 500 error, most likely because the server is down
        UnexpectedException
            The server returned a response code that is not handled
        """
        parameters = {
            "userID": public_userid,
            "adminUserID": self.user_id,
            "enabled": "true" if enabled else "false",
        }
        url = self.base_url + "/api/addUserAsVIP"
        response = self.session.post(url, params=parameters)
        raise_request_exception(response)

    @cache(max_entries=300)  # 5 minutes
    def search_for_user(
        self, user_name: str, exact: bool = False
    ) -> List[SearchedUser]:
        """Searches for a user based on their name.

        Parameters
        ----------
        user_name : str
            The name of the user to search for
        exact : bool, optional
            Whether to only return exact matches or not, by default False

        Returns
        -------
        List[SearchedUser]
            A list of searched users, they have a name and a id attribute

        Raises
        ------
        InvalidJSONException
            The server returned invalid JSON
        ServerException
            The server returned a 500 error, most likely because the server is unavailable.
        NotFoundException
            The user specified was not found.
        BadRequest
            The server returned a 400 error, most likely because your inputs are wrong/impossible or exceeds the maximum allowed size.
        UnexpectedException
            The server returned a response that was not 200, 400, or 500.

        Examples
        --------
        >>> import sponsorblock as sb
        >>> client = sb.Client("your local user id")
        >>> client.search_for_user(user_name="WasiMaster", exact=True)
        [
            SearchedUser(name=WasiMaster, id=a66d1147ad5ee1f4c8950767e430012e3e48451b6dd7f97377bfcafe4954e90d),
            SearchedUser(name=WasiMaster, id=44265cd70f468dab018577e74db13c38fa8e2784f6be54a3f0bb119648489d55)
        ]
        """
        parameters = {"username": user_name, "exact": exact}
        url = self.base_url + "/api/userID"
        response = self.session.get(url, params=parameters)

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise InvalidJSONException(
                "The server returned invalid JSON", response
            ) from exc
        else:
            return [SearchedUser(d) for d in data]
        finally:
            raise_request_exception(response)
