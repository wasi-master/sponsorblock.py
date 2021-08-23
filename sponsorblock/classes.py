from datetime import timedelta
from functools import reduce
import operator


class Segment:
    def __init__(self, category, start, end, uuid, duration, action_type, *, data=None):
        self.category = category
        self.start = start
        self.end = end
        self.uuid = uuid
        self.duration = duration
        self.action_type = action_type
        self.data = data

    @classmethod
    def from_json(cls, data: dict):
        """Generates a Segment object from a JSON dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the segment data.

        Returns
        -------
        Segment
            The segment object gotten form the data.
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
