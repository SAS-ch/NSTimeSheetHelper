# Read Telegram Api key from file
def read_key():
    with open('../secure/token.txt', 'r') as f:
        key = f.readline()
    return key


def read_libre_office_path():
    with open('../settings/libre_office_path.txt', 'r') as f:
        path = f.readline()
    return path
