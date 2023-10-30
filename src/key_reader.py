# Read Telegram Api key from file
def read_key():
    with open('../secure/token.txt', 'r') as f:
        key = f.readline()
    return key
