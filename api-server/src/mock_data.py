import dao.user as user_db

# example_user = {
#     'username': 'test',
#     'sensors': ['be6aa32f-71dd-4c82-b84d-8ed6ea3d9f7d']
# }

example_user = {
    'username': 'test2',
    'sensors': ['6760e42f-c187-40a1-9196-d35b2621ee46']
}

print(user_db.create_user(example_user))
