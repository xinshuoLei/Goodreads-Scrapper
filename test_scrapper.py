import unittest
import json

from bson import is_valid
from database import *
from book_scrapper import *
from author_scrapper import *
from scrapper import *
from main import *

'''
This file contains all unit test for scrapper
'''

class ScrapperTest(unittest.TestCase):

    def test_extract_book_id(self):
        ''' check if the find_id_in_url function can correctly extract book id
        '''
        test_scrapper = Scrapper("https://www.goodreads.com/"
        + "book/show/9648068-the-first-days", 1, 1)
        id = test_scrapper.find_id_in_url("https://www.goodreads.com/"
        + "book/show/9648068-the-first-days")
        self.assertEqual(id, "9648068")
    
    def test_extract_author_id(self):
        ''' check if the find_id_in_url function can correctly extact author id
        '''
        test_scrapper = Scrapper("https://www.goodreads.com/book/show/18586621-"
        "until-the-end-of-the-world", 1, 1)
        id = test_scrapper.find_id_in_url("https://www.goodreads.com/author/show/"
        + "7171979.Sarah_Lyons_Fleming")
        self.assertEqual(id, "7171979")

    def test_check_valid_url(self):
        ''' check if_url_is_valid function can return a response for valid url
        '''
        result = check_if_url_valid("https://www.goodreads.com/"
        + "book/show/9648068-the-first-days")
        self.assertNotEqual(None, result)

    def test_check_valid_author_url(self):
        ''' check if_url_is_valid function return None for author page url
        '''
        result = check_if_url_valid("https://www.goodreads.com/author/show/" +
        "1443712.Carrie_Ryan")
        self.assertEqual(None, result)
        
    def test_check_404_url(self):
        ''' check if_url_is_valid function return None for url
        that does not exist
        '''
        result = check_if_url_valid("https://www.goodreads.com/author/show/1442." +
        "Carrie_Ryan")
        self.assertEqual(None, result)
        

    def test_check_malformed_url(self):
        ''' check if_url_is_valid function return None for malformed url
        '''
        result = check_if_url_valid("goodreads.com/author/show/1443712." +
        "Carrie_Ryan")
        self.assertEqual(None, result)

    def test_check_insert_into_database(self):
        ''' test the insert function does insert data into database
        '''
        client = database.connect_to_server()
        original_size = client["goodreads"]["test"].count_documents({})
        if client is not None:
            database.insert_data(False, True, {"test_key": "1"}, client)
            current_size = client["goodreads"]["test"].count_documents({})
            self.assertEqual(original_size+1, current_size)
            database.close_client(client)

    def test_already_exists_true(self):
        ''' test the already_exist() function in database return true for an
        id that already exist
        '''
        client = database.connect_to_server()
        if client is not None:
            id = database.insert_data(False, True, {"test_key": "2"}, client)
            self.assertEqual(True, already_exist(id.inserted_id, False, True, client))
            database.close_client(client)

    def test_already_exists_false(self):
        ''' test the already_exist() function in database return false for an
        id that does not exist
        '''
        client = database.connect_to_server()
        if client is not None:
            self.assertEqual(False, already_exist("4", False, True, client))
            database.close_client(client)
    
    def test_output_valid_json(self):
        ''' test database output is a valid json
        '''
        client = database.connect_to_server()
        database.output_data(True, client)
        database.close_client(client)
        self.assertEqual(True, self.is_valid_json())

    def is_valid_json(self):
        with open("data.json") as f:
            try: json_object = json.load(f)
            except ValueError as e:
                print("here")
                return False
            return True
        
if __name__ == "__main__":
    unittest.main()
