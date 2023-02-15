import os
import datetime
import bson
from model import Group, Groups, JSONEncoder
import motor.motor_asyncio
import certifi

mongo_user = os.environ['MONGODB_USER']
mongo_pass = os.environ['MONGODB_PASS']
mongo_url = os.environ['MONGODB_URL']

MONGODB_CONNECTION_STRING = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_url}/test:27017"

ASCENDING_SORT = 1
DECENDING_SORT = -1

ca = certifi.where()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING, tlsCAFile=ca)
db = client.groups
col = db.stored_groups


async def fetch_group(title="", areas=[], categories=[], offset=0, page_size=50):
    filters = {}
    documents = []
    if any([title, areas, categories]):
        title = title or ""
        areas = areas or []
        categories = categories or []
        filters = {"$or": [{"category": {"$in": categories}}, {"area": {"$in": areas}}, {"group_name": f"/{title}/"}]}
    
    async for doc in col.find(filters).sort([("category", ASCENDING_SORT), ("_id", DECENDING_SORT)]).skip(offset).limit(page_size):
        group = Group(**doc, group_id=str(doc["_id"]))
        documents.append(group)
    return Groups(groups=documents)

async def add_group(title, area, category, link, description, collection=col):
    filters = {"category": category, "area": area, "group_name": title, "group_link": link}
    update = {
        "$setOnInsert": {
            "category": category,
            "area": area,
            "group_name": title,
            "group_link": link,
        },
        "$set": {
            "insert_time": datetime.datetime.utcnow(),
            "description": description
        }
    }
    doc = await collection.update_one(filters, update=update, upsert=True)
    print(f"doc.upserted_id - {doc.upserted_id}")
    return bool(doc.upserted_id)

async def distinct_values(field):
    values = []
    try:
        values = await col.distinct(field)
    except Exception as e:
        print(e)
    return values

async def get_pending_groups():
    pending_groups_col = db.pending_groups
    documents = []

    async for doc in pending_groups_col.find().sort([("category", ASCENDING_SORT), ("_id", DECENDING_SORT)]):
        group = Group(**doc, group_id=str(doc["_id"]))
        documents.append(group)

    return Groups(groups=documents)

async def pending_group_response(group_id, approve: bool):
    pending_groups_col = db.pending_groups
    documents = []

    filters = {"_id": bson.ObjectId(group_id)}

    doc = await pending_groups_col.find_one(filters)
    if not doc:
        raise Exception(f"Group id {group_id} is invalid")

    group = Group(**doc, group_id=str(doc["_id"]))
    print(group)
    if approve:
        added = await add_group(group.group_name, group.area, group.category, group.group_link, group.description)
        if added:
            print("Added approved group")
        else:
            print("Failed to add approved group")
    
    deleted = await pending_groups_col.delete_one({"_id": bson.ObjectId(doc["_id"])})
    print(f"deleted pending group - {doc['_id']}")
    return deleted.deleted_count == 1

async def add_pending_group(group_name, group_link, area, category, description):
    pending_groups_col = db.pending_groups
    return await add_group(group_name, area, category, group_link, description, collection=pending_groups_col)

async def get_admin_user(creds):
    admin_db = client.users
    col = admin_db.users
    admin_user = await col.find_one({"creds": creds, "role": "admin"})
    return admin_user