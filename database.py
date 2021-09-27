from os import close
import pymongo
from bson.json_util import *


def connect_to_server():
    ''' try to connect to server

    Return: client. None if connection fail
    '''
    client = pymongo.MongoClient("mongodb+srv://lei:cs@goodreads.nwsm6.mongodb.net/")
    try:
        #The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return client
    except pymongo.errors.ConnectionFailure:
        print("Server not available")
        return None
    

'''
This file contains function that insert data into database
and retrieve data from database
'''
def insert_data(is_author, data, client):
    ''' insert data into database

    Args:
        is_author: true if the data is about author, false if data is about book
        data: a dictionary containing the book data to insert 
        client: client to use
    '''
    if client is None:
        return 

    db = client["goodreads"]
    collection = db["book"]
    if (is_author):
        collection = db["author"]
    collection.insert_one(data)

def output_data(is_author, client):
    ''' output data into a json file

    Args:
        is_author: true if the output is about authors. false otherwise
    '''
    if client is None:
        return
    
    db = client["goodreads"]
    collection = db["book"]
    if (is_author):
        collection = db["author"]
    cursor = collection.find()
    list_cur = list(cursor)
    json_data = dumps(list_cur, indent=2)
    with open("data.json", "w") as file:
        file.write(json_data)

def already_exist(id, is_author, client):
    ''' check if id already exist

    Args:
        id: id to check
        is_author: true if check in author table. false otherwise
        client: client to use
    '''
    if client is None:
        return
    
    db = client["goodreads"]
    collection = db["book"]
    if is_author:
        collection = db["author"]
    
    if collection.find({"_id" : id}).limit(1).count() != 0:
        return True

    return False

def close_client(client):
    ''' close client

    Args:
        client: client to close
    '''

    if client is None:
        return 

    client.close()


if __name__ == "__main__":
    client = connect_to_server()
    print(already_exist(1, False, client))
    close_client(client)

