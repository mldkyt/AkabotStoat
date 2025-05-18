import os

REVOLT_TOKEN = os.getenv("REVOLT_TOKEN")

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")

def validate_values(l: dict[str, str | None]):
    for k, v in l.items():
        if v is None:
            print(f"CONSTANTS: The constant value for {k} is NOT set!")

validate_values({
    'REVOLT_TOKEN': REVOLT_TOKEN,
    'MONGODB_HOST': MONGODB_HOST,
    'MONGODB_PORT': MONGODB_PORT,
    'MONGODB_DB': MONGODB_DB,
    'MONGODB_USER': MONGODB_USER,
    'MONGODB_PASSWORD': MONGODB_PASSWORD
})
