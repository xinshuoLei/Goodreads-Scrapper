'''
This file contains the main function, which check command line arguments
and run corresponding functions
'''
import argparse
import requests
from scrapper import *
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-scrap", nargs=3)
    parser.add_argument("-output", nargs=1)
    args = vars(parser.parse_args())

    # program was run with flag scrap
    if (args["scrap"] is not None):
        scrap_args = args["scrap"]
        url = scrap_args[0];
        num_books = int(scrap_args[1])
        num_authors = int(scrap_args[2])
        
        result = check_if_url_valid(url)
        if (result is None):
            print("invalid url")
        else:
            print("valid")
            scrapper = Scrapper(url, num_books, num_authors)
            scrapper.initial_scrap()
            
        if (num_books > 200 or num_authors > 2):
            print("warning: this is a really large number to scarp")
    
    elif (args["output"] is not None):
        output_arg = args["output"][0]
        if (output_arg == "author"):
            client = database.connect_to_server()
            if client is not None:
                database.output_data(True, client)
            database.close_client(client)
            print("output table author to data.json")
        elif (output_arg == "book"):
            client = database.connect_to_server()
            if client is not None:
                database.output_data(False, client)
            database.close_client(client)
            print("output table book to data.json")
        else:
            print("invalid argument")

        
