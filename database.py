
import pymongo

from constants import MONGODB_USER, MONGODB_PASSWORD, MONGODB_HOST, MONGODB_PORT, MONGODB_DB

client = pymongo.MongoClient(
    f'mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/', 27017)[MONGODB_DB]