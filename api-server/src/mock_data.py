import dao.user as user_db

example_user = {
    'username': 'test1',
    'sensors': ['be6aa32f-71dd-4c82-b84d-8ed6ea3d9f7d']
}

print(user_db.create_user(example_user))
