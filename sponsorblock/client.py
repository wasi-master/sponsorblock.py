import requests
from typing import List
from .classes import Segment
from .errors import HTTPException, InvalidJSONError
import json
import re

VIDEO_ID_REGEX = re.compile(r"((?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/))?([^\"&?\/\s]{11})")
ALL_CATEGORIES = ['sponsor', 'selfpromo', 'interaction', 'intro', 'outro', 'preview', 'music_offtopic']

class Client:
    def __init__(self, *, base_url: str=None, debug: bool=False, default_categories: List[str]=None):
        """A client for making requests to the sponsorblock server.

        Parameters
        ----------
        base_url : str, optional
            The url to send the requests to, by default https:
        debug : bool, optional
            Whether to log debug information, by default False
        default_categories : List[str], optional
            The default categories to use, by default [sponsor, selfpromo, interaction, intro, outro, preview, music_offtopic]
        """
        self.base_url = base_url or "https://sponsor.ajay.app"
        self.debug = debug
        self.default_categories = default_categories or ALL_CATEGORIES

    def get_skip_segments(self, video_id: str, *, category: str=None, categories: List[str]=None, required_segments: List[str]=None, service: str="YouTube") -> List[Segment]:
        """Gets the skip segments for a given video.

        Parameters
        ----------
        video_id : str
            The id of the video to get the skip segments for.
        category : str
            A category to get skip segments for. See https://github.com/ajayyy/SponsorBlock/wiki/Types#category
        categories : List[str]
            A list of categories to get the skip segments for. See https://github.com/ajayyy/SponsorBlock/wiki/Types#category
        required_segments : List[str]
            A list of segment UUIDs to require be retrieved, even if they don't meet the minimum vote threshold.
        service : str
            The service to use, default is 'YouTube'. See https://github.com/ajayyy/SponsorBlock/wiki/Types#service.

        Returns
        -------
        List[Segment]
            A list of segments of the video

        Raises
        ------
        ValueError
            The video id is invalid
        InvalidJSONError
            The server returned invalid JSON
        """
        if len(video_id) != 11:
            video_id = VIDEO_ID_REGEX.match(video_id)
            if not video_id:
                raise ValueError("Invalid video id")
        parameters = {
            "videoID": video_id,
            "category": categories or self.default_categories,
            "requiredSegment": required_segments or [],
            "service": service
        }
        if category:
            parameters["category"] = category
        url = self.base_url + '/api/skipSegments'
        response = requests.get(url, params=parameters)
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            raise InvalidJSONError("The server returned invalid JSON", response)
        else:
            if response.status_code != 200:
                raise HTTPException("The server returned a status code".format(response.status_code), response)
            return [Segment.from_json(data) for data in data]

class AsyncClient:
    raise NotImplementedError()