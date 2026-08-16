from database.db import get_user


def fetch_user(user_id):
    return get_user(user_id)
def delete_user(user_id):
    return f"Deleted user {user_id}"