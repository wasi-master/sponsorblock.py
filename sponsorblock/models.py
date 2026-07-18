import operator
from datetime import datetime, timedelta
from functools import reduce
from typing import Optional, Union

from .utils import Category


class Segment:
    """
    A skip segment

    Attributes
    ----------
    category : Category
        The category of the segment
    start : float
        The start time of the segment
    end : float
        The end time of the segment
    uuid : Optional[str], optional
        The uuid of the segment, by default None
    duration : Optional[timedelta], optional
        The duration of the segment, by default None
    action_type : Optional[str], optional
        The action_type of the segment, by default None
    description : Optional[str], optional
        The chapter title for chapter segments, an empty string for other segments
    locked : Optional[int], optional
        Whether the segment is locked, only available for segments gotten from the API
    votes : Optional[int], optional
        The amount of votes on the segment, only available for segments gotten from the API
    video_duration : Optional[float], optional
        The duration of the video when the segment was submitted, only available for segments gotten from the API
    data : Optional[dict], optional
        The raw data that was used to create the segment, can be None if the segment was created manually

    Note
    ----
    While creating your own instance you should only pass the category, start, end time and
    optionally the action_type and description (for chapters).
    The other attributes won't do anything, those are only useful for segments gotten from the API.
    """

    def __init__(
        self,
        category: Category,
        start: Union[float, timedelta],
        end: Union[float, timedelta],
        uuid: Optional[str] = None,
        duration: Optional[timedelta] = None,
        action_type: Optional[str] = None,
        *,
        description: Optional[str] = None,
        locked: Optional[int] = None,
        votes: Optional[int] = None,
        video_duration: Optional[float] = None,
        data: Optional[dict] = None,
    ):
        """A skip segment

        Parameters
        ----------
        category : Category
            The category of the segment
        start : float, timedelta
            The start time of the segment
        end : float, timedelta
            The end time of the segment
        action_type : str, optional
            The action type of the segment (``skip``, ``mute``, ``full``, ``poi``, ``chapter``)
        description : str, optional
            The chapter title, only used for chapter segments
        """
        self.category = category
        self.start = start
        self.end = end
        self.uuid = uuid
        self.duration = duration
        self.action_type = action_type
        self.description = description
        self.locked = locked
        self.votes = votes
        self.video_duration = video_duration
        self.data = data

    @classmethod
    def from_dict(cls, data: dict):
        """Generates a Segment object from a JSON dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the segment data.

        Returns
        -------
        Segment
            The segment object gotten form the data.

        Warning
        -------
        This should not be used manually, this is for the library
        """
        category = data["category"]
        start, end = data["segment"]
        uuid = data["UUID"]
        duration = timedelta(seconds=reduce(operator.sub, reversed(data["segment"])))
        action_type = data.get("actionType")
        return cls(
            category,
            start,
            end,
            uuid,
            duration,
            action_type,
            description=data.get("description"),
            locked=data.get("locked"),
            votes=data.get("votes"),
            video_duration=data.get("videoDuration"),
            data=data,
        )

    def __repr__(self):
        return (
            f"Segment(category={self.category}, start={self.start}, end={self.end}, "
            f"uuid={self.uuid}, duration={self.duration}, action_type={self.action_type})"
        )


class User:
    """A user

    Attributes
    ----------
    user_id : str
        The id of the user
    user_name : str
        The name of the user
    minutes_saved : int
        The amount of minutes saved by the user
    segment_count : int
        The amount of segments created by the user
    ignored_segment_count : int
        The amount of segments that were ignored by the user
    view_count : int
        The amount of views by the user
    ignored_view_count : int
        The amount of views that were ignored by the user
    warnings : int
        The amount of warnings the user has
    reputation : int
        The amount of reputation the user has
    vip : bool
        Whether the user is a VIP
    last_segment_id : str
        The id of the last segment created by the user

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.user_id = data["userID"]
        self.user_name = data["userName"]
        self.minutes_saved = data["minutesSaved"]
        self.segment_count = data["segmentCount"]
        self.ignored_segment_count = data["ignoredSegmentCount"]
        self.view_count = data["viewCount"]
        self.ignored_view_count = data["ignoredViewCount"]
        self.warnings = data["warnings"]
        self.reputation = data["reputation"]
        self.vip = data["vip"]
        self.last_segment_id = data["lastSegmentID"]

    def __repr__(self):
        return (
            f"User(user_id={self.user_id}, user_name={self.user_name}, "
            f"minutes_saved={self.minutes_saved}, segment_count={self.segment_count}, "
            f"ignored_segment_count={self.ignored_segment_count}, view_count={self.view_count}, "
            f"ignored_view_count={self.ignored_view_count}, warnings={self.warnings}, "
            f"reputation={self.reputation}, vip={self.vip}, last_segment_id={self.last_segment_id})"
        )


class UserStats:
    """Stats for a user, gotten from the userStats API

    Attributes
    ----------
    user_id : str
        The public id of the user
    user_name : str
        The name of the user
    minutes_saved : float
        The amount of minutes saved by the user's segments
    segment_count : int
        The amount of segments created by the user
    category_counts : Optional[dict]
        A mapping of category name to the number of segments the user submitted in
        that category. Only available if fetch_category_stats was True
    action_type_counts : Optional[dict]
        A mapping of action type name to the number of segments the user submitted with
        that action type. Only available if fetch_action_type_stats was True

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.user_id = data["userID"]
        self.user_name = data["userName"]
        self.minutes_saved = data["overallStats"]["minutesSaved"]
        self.segment_count = data["overallStats"]["segmentCount"]
        self.category_counts = data.get("categoryCount")
        self.action_type_counts = data.get("actionTypeCount")

    def __repr__(self):
        return (
            f"UserStats(user_id={self.user_id}, user_name={self.user_name}, "
            f"minutes_saved={self.minutes_saved}, segment_count={self.segment_count}, "
            f"category_counts={self.category_counts}, action_type_counts={self.action_type_counts})"
        )


class TopUser:
    """
    A top user.

    Attributes
    ----------
    user_name : str
        The name of the user
    view_count : int
        The total number of views of the user's segments
    total_submissions : int
        The total number of submissions the user has made
    minutes_saved : float
        The amount of time the user has saved

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(
        self,
        user_name: str,
        view_count: int,
        total_submissions: int,
        minutes_saved: float,
    ):
        self.user_name = user_name
        self.view_count = view_count
        self.total_submissions = total_submissions
        self.minutes_saved = minutes_saved

    def __repr__(self):
        return (
            f"TopUser(user_name={self.user_name}, view_count={self.view_count}, "
            f"total_submissions={self.total_submissions}, minutes_saved={self.minutes_saved})"
        )


class TotalStats:
    """The total stats

    Attributes
    ----------
    user_count : int
        The amount of users, only available if count_contributing_users was true
    active_users : int
        Sum of public install stats from Chrome webstore and Firefox addons store
    api_users : int
        48-hour active API users
    view_count : int
        The total number of views
    total_submissions : int
        The total number of submissions
    minutes_saved
        The total amount of time saved

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data):
        self.user_count = data["userCount"] if "userCount" in data else None
        self.active_users = data["activeUsers"]
        self.api_users = data["apiUsers"]
        self.view_count = data["viewCount"]
        self.total_submissions = data["totalSubmissions"]
        self.minutes_saved = data["minutesSaved"]

    def __repr__(self):
        return (
            f"TotalStats(user_count={self.user_count}, active_users={self.active_users}, "
            f"api_users={self.api_users}, view_count={self.view_count}, "
            f"total_submissions={self.total_submissions}, minutes_saved={self.minutes_saved})"
        )


class SegmentInfo:
    """A class representing the segment info

    Attributes
    ----------
    video_id : str
        The id of the video
    start_time : float
        The start time of the segment
    end_time : float
        The end time of the segment
    votes : int
        The amount of votes the segment has
    locked : int
        Whether the segment is locked
    uuid : str
        The uuid of the segment
    user_id : str
        The id of the user that created the segment
    time_submitted : datetime.datetime
        The time the segment was submitted
    views : int
        The amount of views the segment has
    category : str
        The category of the segment
    action_type : str
        The action type of the segment
    service : str
        The service of the segment
    video_duration : float
        The duration of the video
    hidden : int
        Whether the segment is hidden (2 downvotes or downvoted by a VIP)
    reputation : int
        The reputation of the submitter at the time of submission
    shadow_hidden : int
        Whether the submitter is shadowbanned
    hashed_video_id : str
        The hashed video id of the video
    user_agent : str
        The user agent of the segment
    description : str
        The chapter title for chapter segments, an empty string for other segments

    Note
    ----
    Some attributes can be None when the segment info came from
    :meth:`sponsorblock.client.Client.search_segments`, since that endpoint
    returns fewer fields.

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data):
        self.video_id = data.get("videoID")
        self.start_time = data["startTime"]
        self.end_time = data["endTime"]
        self.votes = data["votes"]
        self.locked = data["locked"]
        self.uuid = data["UUID"]
        self.user_id = data["userID"]
        time_submitted = data.get("timeSubmitted")
        self.time_submitted = (
            datetime.fromtimestamp(time_submitted / 1000)
            if time_submitted is not None
            else None
        )
        self.views = data["views"]
        self.category = data["category"]
        self.action_type = data.get("actionType")
        self.service = data.get("service")
        self.video_duration = data.get("videoDuration")
        self.hidden = data.get("hidden")
        self.reputation = data.get("reputation")
        self.shadow_hidden = data.get("shadowHidden")
        self.hashed_video_id = data.get("hashedVideoID")
        self.user_agent = data.get("userAgent")
        self.description = data.get("description")

    def __repr__(self):
        return (
            f"SegmentInfo(video_id={self.video_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, votes={self.votes}, locked={self.locked}, "
            f"uuid={self.uuid}, user_id={self.user_id}, time_submitted={self.time_submitted}, "
            f"views={self.views}, category={self.category}, action_type={self.action_type}, "
            f"service={self.service}, video_duration={self.video_duration}, "
            f"hashed_video_id={self.hashed_video_id}, user_agent={self.user_agent})"
        )


class LockedCategories:
    """The locked categories of a video

    Attributes
    ----------
    categories : List[str]
        The categories that are locked for the video
    reason : str
        The reason for the lock, only the most recent reason is available
    action_types : Optional[List[str]]
        The action types the lock applies to, not available when gotten with a hash
    video_id : Optional[str]
        The id of the video, only available when gotten with a hash
    hash : Optional[str]
        The full hash of the video id, only available when gotten with a hash

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.categories = data["categories"]
        self.reason = data.get("reason", "")
        self.action_types = data.get("actionTypes")
        self.video_id = data.get("videoID")
        self.hash = data.get("hash")

    def __repr__(self):
        return (
            f"LockedCategories(categories={self.categories}, reason={self.reason}, "
            f"action_types={self.action_types}, video_id={self.video_id})"
        )


class LockReason:
    """The lock status and reason of a category on a video

    Attributes
    ----------
    category : str
        The category the lock applies to
    locked : int
        The status of the lock
    reason : str
        The reason for the lock
    user_id : str
        The public id of the VIP that locked the category
    user_name : str
        The username of the VIP that locked the category

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.category = data["category"]
        self.locked = data["locked"]
        self.reason = data["reason"]
        self.user_id = data["userID"]
        self.user_name = data["userName"]

    def __repr__(self):
        return (
            f"LockReason(category={self.category}, locked={self.locked}, "
            f"reason={self.reason}, user_id={self.user_id}, user_name={self.user_name})"
        )


class ServerStatus:
    """The status of the sponsorblock server

    Attributes
    ----------
    uptime : float
        The uptime of the server in seconds
    commit : str
        The full SHA hash of the latest git commit of the server
    db : int
        The current database version
    start_time : int
        The unix time in milliseconds that the request was received
    process_time : int
        The delay in milliseconds between the database request being made and the response being received
    redis_process_time : Optional[int]
        The delay in milliseconds between the redis request being made and the response being received
    load_average : List[float]
        The 5 and 15 minute load averages of the server
    status_requests : int
        The number of status requests made in the last minute
    hostname : str
        The hostname of the server that answered the request
    data : dict
        The raw response, useful for any extra fields the server might return

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.uptime = data.get("uptime")
        self.commit = data.get("commit")
        self.db = data.get("db")
        self.start_time = data.get("startTime")
        self.process_time = data.get("processTime")
        self.redis_process_time = data.get("redisProcessTime")
        self.load_average = data.get("loadavg")
        self.status_requests = data.get("statusRequests")
        self.hostname = data.get("hostname")
        self.data = data

    def __repr__(self):
        return (
            f"ServerStatus(uptime={self.uptime}, commit={self.commit}, db={self.db}, "
            f"start_time={self.start_time}, process_time={self.process_time}, "
            f"load_average={self.load_average}, hostname={self.hostname})"
        )


class SegmentSearchResults:
    """The results of a segment search

    Attributes
    ----------
    segment_count : int
        The total number of segments matching the query
    page : int
        The page number of these results
    segments : List[SegmentInfo]
        The segments on this page, at most 10

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data: dict):
        self.segment_count = data["segmentCount"]
        self.page = data["page"]
        self.segments = [SegmentInfo(segment) for segment in data["segments"]]

    def __repr__(self):
        return (
            f"SegmentSearchResults(segment_count={self.segment_count}, "
            f"page={self.page}, segments={self.segments})"
        )


class SearchedUser:
    """A user gotten by searching for his name

    Attributes
    ----------
    name : str
        The name of the user
    id : str
        The id of the user

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data):
        self.name = data["userName"]
        self.id = data["userID"]
        self.user_id = self.id

    def __repr__(self):
        return f"SearchedUser(name={self.name}, id={self.id})"
