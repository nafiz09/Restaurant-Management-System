def generate_primary_key(id):
    if id is not None:
        id = id + 1
    else:
        id = 1
    return id
