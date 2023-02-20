import os
import json
import jwt
import inspect
from functools import wraps

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

import database
from model import JSONEncoder
from api_requests import *

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def admin_access(f):
    @wraps(f)
    async def foo(msg):
        admin_user = await database.get_admin_user(msg.token)
        if not admin_user:
            raise Exception("No access") 

        if inspect.iscoroutinefunction(f):
            return await f(msg)
        return f(msg)

    return foo

@app.get("/")
def read_root():
    return {"Ping": "Pong"}


@app.post("/api/groups/")
async def get_groups(msg: GetGroupsRequest):
    response = await database.fetch_group(msg.title, msg.areas, msg.categories, msg.offset, msg.page_size)
    return response.serialize()

@app.post("/api/pending_groups/")
@admin_access
async def get_pending_groups(msg: FetchPendingGroupRequest):
    response = await database.get_pending_groups()
    return response.serialize()

@app.post("/api/pending_groups/response")
@admin_access
async def response_pending_group(msg: PendingGroupResponseRequest):
    response = await database.pending_group_response(msg.group_id, msg.approve)
    return ResponsePendingGroupResponse(success=response)

@app.post("/api/delete_group")
@admin_access
async def delete_group(msg: DeleteGroupRequest):
    response = await database.delete_group(msg.group_id)
    return DeleteGroupResponse(success=response)

@app.post("/api/update_group")
@admin_access
async def update_group(msg: UpdateGroupRequest):
    response = await database.update_group(msg.group_id, msg.group_name, msg.group_link, msg.area, msg.category)
    return UpdateGroupResponse(success=response)

@app.post("/api/pending_groups/add")
async def add_pending_group(msg: AddPendingGroupRequest):
    response = await database.add_pending_group(msg.group_name, msg.group_link, msg.area, msg.category, msg.description)
    return AddPendingGroupResponse(success=response)

@app.post("/api/distinct/")
async def distinct(msg: GetDistinctRequest):
    response = await database.distinct_values(msg.field)
    return json.dumps(response)

@app.post("/login")
async def login_admin(login_item: LoginItem):
    data = jsonable_encoder(login_item)
    secret = os.environ['KEY_SECRET']
    creds = jwt.encode(data, secret, algorithm="HS256")
    admin_user = await database.get_admin_user(creds)
    return JSONEncoder().encode(admin_user) 
