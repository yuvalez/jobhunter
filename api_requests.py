from typing import Union
from pydantic import BaseModel

class Msg(BaseModel):
    areas: Union[list[str], None]
    title: Union[str, None]
    categories: Union[list[str], None]


class GetGroupsRequest(Msg):
    offset: int = 0
    page_size: int = 50


class GetDistinctRequest(BaseModel):
    field: str


class LoginItem(BaseModel):
    username: str
    password: str

class AdminAcessRequest(BaseModel):
    token: str

class FetchPendingGroupRequest(AdminAcessRequest):
    pass

class AddPendingGroupRequest(BaseModel):
    group_name: str
    group_link: str
    area: str
    category: str
    description: Union[str, None]

class AddPendingGroupResponse(BaseModel):
    success: bool

class ResponsePendingGroupResponse(BaseModel):
    success: bool

class PendingGroupResponseRequest(AdminAcessRequest):
    group_id: str
    approve: bool
