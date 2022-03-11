import config.db as db
import dao.utils as utils

def get_all():
    data = list(db.user.find({}))
    serialised_data = utils.serialize(data)

    return serialised_data

def get_user(username):
    data = db.user.find_one({'username': username})
    return utils.serialize(data)


def create_user(user):
    return db.user.insert_one(user)