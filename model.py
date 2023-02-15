import datetime
from typing import Union

from pydantic import BaseModel

import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Group):
            return o.__dict__
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Group(BaseModel):
    group_id: str
    category: str
    group_name: str
    area: Union[str, None]
    group_link: str
    insert_date: Union[datetime.datetime, None]
    description: Union[str, None]


class Groups(BaseModel):
    groups: list[Group]

    def serialize(self):
        return JSONEncoder().encode(self.groups)