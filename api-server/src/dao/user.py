import config.db as db
import dao.utils as utils

def get_all():
    data = list(db.user.find({}))

    return utils.parse_json(data)

def get_user(username):
    data = db.user.find_one({'username': username})
    return utils.parse_json(data)


def create_user(user):
    return db.user.insert_one(user)

def update_user(username, updated_fields):
    result = db.user.update_one({"username": username}, {"$set": updated_fields})
    return {"matched": result.matched_count, "modified": result.modified_count}