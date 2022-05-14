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
    data : Optional[dict], optional
        The raw data that was used to create the segment, can be None if the segment was created manually

    Note
    ----
    While creating your own instance you should only pass the category, start and end time.
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
        """
        self.category = category
        self.start = start
        self.end = end
        self.uuid = uuid
        self.duration = duration
        self.action_type = action_type
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
        action_type = data["actionType"]
        return cls(category, start, end, uuid, duration, action_type, data=data)

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
    hashed_video_id : str
        The hashed video id of the video
    user_agent : str
        The user agent of the segment

    Warning
    -------
    You should not make a instance of this yourself, this should only be created by the libray
    """

    def __init__(self, data):
        self.video_id = data["videoID"]
        self.start_time = data["startTime"]
        self.end_time = data["endTime"]
        self.votes = data["votes"]
        self.locked = data["locked"]
        self.uuid = data["UUID"]
        self.user_id = data["userID"]
        self.time_submitted = datetime.fromtimestamp(data["timeSubmitted"] / 1000)
        self.views = data["views"]
        self.category = data["category"]
        self.service = data["service"]
        self.video_duration = data["videoDuration"]
        self.hidden = data["hidden"]
        self.reputation = data["reputation"]
        self.shadow_hidden = data["shadowHidden"]
        self.hashed_video_id = data["hashedVideoID"]
        self.user_agent = data["userAgent"]

    def __repr__(self):
        return (
            f"SegmentInfo(video_id={self.video_id}, start_time={self.start_time}, "
            f"end_time={self.end_time}, votes={self.votes}, locked={self.locked}, "
            f"uuid={self.uuid}, user_id={self.user_id}, time_submitted={self.time_submitted}, "
            f"views={self.views}, category={self.category}, service={self.service}, "
            f"video_duration={self.video_duration}, hashed_video_id={self.hashed_video_id}, "
            f"user_agent={self.user_agent})"
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
