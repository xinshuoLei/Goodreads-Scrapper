import pymongo
from bson.json_util import *

'''
This file contains function that insert data into database
and retrieve data from database
'''
def insert_data(is_author, data):
    ''' insert data into database

    Args:
        is_author: true if the data is about author, false if data is about book
        data: a dictionary containing the book data to insert 
    '''
    client = pymongo.MongoClient("mongodb+srv://lei:cs@goodreads.nwsm6.mongodb.net/")
    try:
        #The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = client["goodreads"]
        collection = db["book"]
        if (is_author):
            collection = db["author"]
        collection.insert_one(data)
        client.close()
    except pymongo.errors.ConnectionFailure:
        print("Server not available")

def output_data(is_author):
    client = pymongo.MongoClient("mongodb+srv://lei:cs@goodreads.nwsm6.mongodb.net/")
    try:
        #The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        db = client["goodreads"]
        collection = db["book"]
        if (is_author):
            collection = db["author"]
        cursor = collection.find()
        list_cur = list(cursor)
        json_data = dumps(list_cur, indent=2)
        with open("data.json", "w") as file:
            file.write(json_data)

    except pymongo.errors.ConnectionFailure:
        print("Server not available")


if __name__ == "__main__":
    client = pymongo.MongoClient("mongodb+srv://Lei:cs@goodreads.nwsm6.mongodb.net/")
    print("here")
    try:
        #The ismaster command is cheap and does not require auth.
        
        print("connected")
        client.close()
    except pymongo.errors.ConnectionFailure:
        print(pymongo.errors.ConnectionFailure)
        print("Server not available")
        client.close()

