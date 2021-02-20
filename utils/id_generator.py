import uuid

def random_int(bits):
    return uuid.uuid1().int >> (128 - bits)

def uuid4():
    return uuid.uuid4()