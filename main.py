'''
This file contains the main function, which check command line arguments
and run corresponding functions
'''
import argparse
import requests
from scrapper import *
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from query_parser import *
from api import *

'''
url prefix for goodreads
'''
GOODREADS_URL = "goodreads.com"

'''
a str used for checking if the page is a book page
'''
BOOK = "book/show"


def check_if_url_valid(url):

    ''' check if the url points to a book page in goodreads and if the url exists
    
    Return: response from request if url is valid. None otherwise
    '''

    # check if url points to a book page in goodreads first
    # avoid making unnecessary request

    validate = URLValidator()
    try:
        validate(url)
        if (BOOK in url and GOODREADS_URL in url):
            response = requests.get(url)
            if response:
                return response
    except ValidationError as exception:
       return None
    
    return None

def write_json_data_to_file(json_data, file_name):
    ''' write json data to file

    Args:
        json_data: json data
        file_name: output filename
    '''
    with open(file_name, "w") as file:
        file.write(json_data)


def handle_scrap(scrap_args):
    ''' function that handle the scrap flag

    Args:
        scrap_args: args for scrap
    '''
    url = scrap_args[0];
    num_books = int(scrap_args[1])
    num_authors = int(scrap_args[2])

    if (num_books > 200 or num_authors > 50):
        print("warning: this is a really large number to scarp")

    result = check_if_url_valid(url)
    if (result is None):
        print("invalid url")
    else:
        print("valid url")
        scrapper = Scrapper(url, num_books, num_authors)
        scrapper.initial_scrap()


def handle_get(id, table):
    ''' functuin that handle the get flag

    Args:
        id: id to get
        table: table to get from
    '''
    client = connect_to_server()
    exist = check_id_exist(table, id, client)

    if exist:
        json_data = get_data_by_id(table, id, client)
        write_json_data_to_file(json_data, "get_result.json")
        print("result output to get_result.json")
    else:
        print("invalid id")
    
    close_client(client)


def handle_output():
    ''' function that handle the output flag

    Args:
        scrap_args: args for output
    '''
    if (output_arg == "author"):
        client = connect_to_server()
        if client is not None:
            output_data(True, client)
        close_client(client)
        print("output table author to data.json")
    elif (output_arg == "book"):
        client = connect_to_server()
        if client is not None:
            output_data(False, client)
        close_client(client)
        print("output table book to data.json")
    else:
        print("invalid argument")
        

def handle_delete(id, table):
    ''' functuin that handle the delete flag

    Args:
        id: id to use
        table: table to delete from
    '''
    client = connect_to_server()
    exist = check_id_exist(table, id, client)

    if exist:
        delete_by_id(table, id, client)
        print("delete successful")
    else:
        print("invalid id")

    close_client(client)

def handle_query(query):
    ''' function that handle the output flag

    Args:
        query: query to handle
    '''
    error = []
    parse_result = parse_whole_argument(query, error)
    if parse_result:
        client = connect_to_server()
        if client is not None:
            json_data = find_and_output(client, parse_result[0], 
                    parse_result[1], False)
            if len(parse_result) != 2:
                json_data = find_and_output(client, parse_result[1], 
                    parse_result[2], True)
            write_json_data_to_file(json_data, "query.json")
            print("output query result to query.json")
        close_client(client)
    else:
        print(error)

def handle_update(id, table, update):
    ''' functuin that handle the delete flag

    Args:
        id: id to use
        table: table to delete from
        update: update to form
    '''
    client = connect_to_server()
    exist = check_id_exist(table, id, client)

    if exist:
        update_dic = loads(update)
        update_data_by_id(table, id, client, update_dic)
        print("update successful")
    else:
        print("invalid id")

    close_client(client)


def check_id_exist(table, id, client):
    ''' helper function to check if an id exist

    Args:
        table: table to check
        id: id to check
        client: client to use
    
    Return:
        True if id exists in table, False otherwise
    '''
    if table == "author":
        if already_exist(id, True, False, client):
            return True
    elif table == "book":
        if already_exist(id, False, False, client):
            return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-scrap", nargs=3, help="arguments: url, num_books, num_authors")
    parser.add_argument("-output", nargs=1, help="argument: book or author")
    parser.add_argument("-query", nargs=1, help="only argument is the query." 
        + " please place query in single quotes")
    parser.add_argument("-get", nargs=2, help="arguments: id, author/book")
    parser.add_argument("-delete", nargs=2, help="arguments: id, author/book")
    parser.add_argument("-update", nargs=3, help="arguments: id, author/book, update"
        + " please put update in quotes")
    args = vars(parser.parse_args())

    # program was run with flag scrap
    if args["scrap"] is not None:
        scrap_args = args["scrap"]
        handle_scrap(scrap_args)
            
    # program was run with output flag
    elif args["output"] is not None:
        output_arg = args["output"][0]
        handle_output()

    # program was run with query flag
    elif args["query"] is not None:
        query = args["query"][0]
        handle_query(query)

    # program was run with get flag
    elif args["get"] is not None:
        handle_get(args["get"][0], args["get"][1])

    # program was run with delete flag
    elif args["delete"] is not None:
        handle_delete(args["delete"][0], args["delete"][1])

    elif args["update"] is not None:
        handle_update(args["update"][0], args["update"][1], args["update"][2])

        
