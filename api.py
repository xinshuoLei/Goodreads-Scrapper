from collections import UserList
from flask import Flask, jsonify, request
from bson.json_util import *
from pymongo import database
from author_scrapper import AuthorScrapper
from book_scrapper import BookScrapper
from database import*
from query_parser import *
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests

app = Flask(__name__)
AUTHOR = "author"
BOOK = "book"
GOODREADS_URL = "https://www.goodreads.com"

def check_if_scrap_url_valid(url):
    ''' check if the url points to a book page in goodreads and if the url exists
    
    Args:
        url: url to check

    Return: response from request if url is valid. None otherwise
    '''

    validate = URLValidator()
    try:
        validate(url)
        print(url)
        if GOODREADS_URL in url and (AUTHOR in url or BOOK in UserList):
            response = requests.get(url)
            if response:
                return response
    except ValidationError as exception:
       return None

    return None


def find_id_in_url(url):
    ''' find id of a book or author from url

    Return:
        id found
    '''
    everything_after_show = url.split("show/")[1]

    id = everything_after_show.split(".")[0]
    if (len(id) == len(everything_after_show)):
        # if split does not have any effect, the url is formatted in another way
        id = everything_after_show.split("-")[0]

    return id


def get_data_by_id(table, id, client):
    ''' get data from database[table] by id

    Args: 
        table: table to get from
        id: id to search
        client: client to use

    Return: json data
    '''
    collection = client["goodreads"][table]

    cursor = collection.find({"_id":id})
    list_cur = list(cursor)
    json_data = dumps(list_cur, indent=2)
    return json_data


def update_data_by_id(table, id, client, update):
    ''' update data from database[table] by id

    Args: 
        table: table to get from
        id: id to search
        client: client to use
        update: the updates to perform

    Return: json data
    '''
    collection = client["goodreads"][table]
    
    # check updates are all valid
    for key in update.keys():
        if key not in ATTRIBUTES[table]:
            error = {"error:" "attribute does not exist"}
            json_data = dumps(error, indent=2)
            return json_data
     
    collection.update_one({"_id": id},  {'$set': update})
    message = {"message": "update successful"}
    json_data = dumps(message, indent=2)
    return json_data



def delete_by_id(table, id, client):
    ''' delete data from database[table] by id

    Args: 
        table: table to delete from
        id: id to search
        client: client to use

    Return:
        json data of success message
    '''
    collection = client["goodreads"][table]
    collection.delete_one({'_id': id})
    message = {"message": "suceesully delete " + id}
    json_data = dumps(message, indent=2)
    return json_data

def handle_single_post(request, is_author):
    ''' handle post request for single file

    Args:
        request: the request
        is_author: True if the resut is on author table

    Return:
        An HTTP response
    '''
    if request.content_type != "application/json":
        resp = jsonify({"message": "Bad Request"})
        resp.status_code = 415
        return resp
            
    # load data from post
    data = json.loads(request.data)
    if data:
        client = connect_to_server()
        if "_id" not in data.keys() or already_exist(data["_id"], 
            is_author, False, client):
            # id already exist or data to insert has no id
            message = {"error": "invalid id"}
        else:
            insert_data(is_author, False, data, client)
            message = {"message": "sucessful put"}
        close_client(client)
        json_data = dumps(message, indent=2)
        resp = jsonify(json_data)
    else:
        # data is blank
        resp = jsonify({'message': 'Bad Request'})
        resp.status_code = 400

    return resp


@app.route('/author', methods=["GET", "POST", "DELETE", "PUT"])
def handle_author():
    """Handles the author route
    
    Return:
        An HTTP response
    """
    for arg in request.args.keys():
        if arg != "id":
            # field other than id are used
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400
            return resp
    
    id = request.args.get('id', None)

    if id:
        client = connect_to_server()
        # report erro if no such id is found
        if not already_exist(id, True, False, client):
            message = {"error": "no such id"}
            json_data = dumps(message, indent=2)
        
        else:
            if request.method == "GET":
                json_data = get_data_by_id(AUTHOR, id, client)
            elif request.method == "DELETE":
                json_data = delete_by_id(AUTHOR, id, client)
            elif request.method == "PUT":
                if request.content_type != "application/json":
                    resp = jsonify({"message": "Bad Request"})
                    resp.status_code = 415
                    return resp
                update = json.loads(request.data)
                if update:
                    json_data = update_data_by_id(AUTHOR, id, client, update)
                else:
                    # data is blank
                    resp = jsonify({'message': 'Bad Request'})
                    resp.status_code = 400
                
        resp = jsonify(json_data)
        close_client(client)
    else:
        # user did not provide id, which is only valid for post request
        if request.method == "POST":
            return handle_single_post(request, True)
            
        else:
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400

    return resp


@app.route('/book', methods=['GET', "POST", "DELETE", "PUT"])
def handle_book():
    """Handles the author route
    
    Return:
        An HTTP response
    """
    for arg in request.args.keys():
        if arg != "id":
            # field other than id are used
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400
            return resp
    
    id = request.args.get('id', None)

    if id:
        client = connect_to_server()
        # report erro if no such id is found
        if not already_exist(id, False, False, client):
            message = {"error": "no such id"}
            json_data = dumps(message, indent=2)
        
        else:
            if request.method == "GET":
                json_data = get_data_by_id(BOOK, id, client)
            elif request.method == "DELETE":
                json_data = delete_by_id(BOOK, id, client)
            elif request.method == "PUT":
                if request.content_type != "application/json":
                    resp = jsonify({"message": "Bad Request"})
                    resp.status_code = 415
                    return resp
                update = json.loads(request.data)
                if update:
                    json_data = update_data_by_id(BOOK, id, client, update)
                else:
                    # data is blank
                    resp = jsonify({'message': 'Bad Request'})
                    resp.status_code = 400

        resp = jsonify(json_data)
        close_client(client)
    else:
        # user did not provide id, which is only valid for post request
        if request.method == "POST":
            return handle_single_post(request, False)
        else:
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400

    return resp


@app.route('/search', methods=['GET'])
def handle_search():
    '''Handles the search route
    
    Return:
        An HTTP response
    '''
    for arg in request.args.keys():
        if arg != "q":
            # field other than q are used
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400
            return resp
    
    query = request.args.get("q", None)
    
    # no q field, set status code to 400
    if query is None:
        resp = jsonify({'message': 'Bad Request'})
        resp.status_code = 400
        return resp
    
    error = []
    parse_result = parse_whole_argument(query, error)

    client = connect_to_server()
    if parse_result:
        json_data = find_and_output(client, parse_result[0], parse_result[1], False)
        if len(parse_result) != 2:
                json_data = find_and_output(client, parse_result[1], 
                parse_result[2], True)
    else: 
        erro_msg = {"error": error}
        json_data = dumps(erro_msg, indent=2)

    resp = jsonify(json_data)    
    return resp


@app.route('/scrape', methods=['POST'])
def handle_scrape():
    '''Handles the scrap route
    
    Return:
        An HTTP response
    '''
    for arg in request.args.keys():
        if arg != "attr":
            # field other than attr are used
            resp = jsonify({'message': 'Bad Request'})
            resp.status_code = 400
            return resp
    
    url = request.args.get('attr', None)

    if url is None:
        resp = jsonify({'message': 'Bad Request'})
        resp.status_code = 400
        return resp

    success = False
    request_response = check_if_scrap_url_valid(url)
    client = connect_to_server()
    if request_response and client:
        id = find_id_in_url(url)
        dic = None
        if BOOK in url:
            if not already_exist(id, False, False, client):
                book_scrapper = BookScrapper(url, id)
                dic = book_scrapper.get_info_dictionary()
                # insert into database
                insert_data(False, False, dic, client)
                success = True
        else:
            if not already_exist(id, True, False, client):
                author_scrapper = AuthorScrapper(url, id)
                dic = author_scrapper.get_info_dictionary()
                # insert into database
                insert_data(True, False, dic, client)
                success = True

    # produce response message
    message = {"error": "failed to scrap"}
    if success:
        message = {"message": "successfully scrap and insert"}
    json_data = dumps(message, indent=2)
    resp = jsonify(json_data)
    
    close_client(client)
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=105)