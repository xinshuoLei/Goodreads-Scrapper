from book_scrapper import *
from author_scrapper import *
import database

''' This file contains the full scrapper
'''
class Scrapper:
    def __init__(self, strating_url, num_books, num_authors):
        ''' initialize a scrapper

        Args:
            starting_url: url of the starting page
            num_books: number of books to scrape
            num_authors: number of authors to scrape
        '''
        self._starting_url = strating_url
        self._num_books = num_books
        self._num_authors = num_authors
        self._client = database.connect_to_server()

        if self._client is None:
            return

        # initial counts are 0
        self._book_count = 0
        self._author_count = 0

        

    def initial_scrap(self):
        # scrap book with start
        book_id = self.find_id_in_url(self._starting_url)
        book = BookScrapper(self._starting_url, book_id)
        book_info = book.get_info_dictionary()
        if not database.already_exist(book_id, False, False, self._client):
            database.insert_data(False, False, book_info, self._client)
            self._book_count += 1
            print("finish scrapping book with id " + book_id)

        author_id = self.find_id_in_url(book_info["author_url"])
        author = AuthorScrapper(book_info["author_url"], author_id)
        author_info = author.get_info_dictionary()

        if not database.already_exist(author_id, True, False, self._client):
            database.insert_data(True, False, author_info, self._client)
            self._author_count += 1

        # save current author since the next book and author to scrap
        # is realted to first author
        self._current_author = author_info

        print("finish scrapping author with id " + author_id)

        self.start_traversing()
        database.close_client(self._client)

        self.start_traversing()
        
        
        
    def find_id_in_url(self, url):
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

    def start_traversing(self):
        ''' start scrapping and stop after scrapping num_books and num_authors
        '''
        while (self._book_count != self._num_books 
            and self._author_count != self._num_authors):

            # upper limit to scrap
            if self._book_count + self._author_count > 2000:
                break

            # get all books of current author first
            author_books = self._current_author["author_books"]
            for book_url in author_books:
                print(book_url)
                if self._book_count >= self._num_books:
                    break
                book_id = self.find_id_in_url(book_url)
                print(book_id)

                # check if book is already scrapped
                if database.already_exist(book_id, False, False, self._client):
                    continue
                    
                book = BookScrapper(book_url, book_id)
                # insert book info into database
                database.insert_data(False, False, book.get_info_dictionary(), self._client)
                self._book_count += 1
                print("finish scrapping book with id " + book_id)
                time.sleep(3)

            # get all related authors
            related_authors = self._current_author["related_authors"]
            for author_url in related_authors:
                if self._author_count >= self._num_authors:
                    break
                author_id = self.find_id_in_url(author_url)

                # check if author is already scrapped
                if database.already_exist(author_id, True, False, self._client):
                    continue

                author = AuthorScrapper(author_url, author_id)
                author_info = author.get_info_dictionary()
                # insert book info into database
                database.insert_data(True, False, author_info, self._client)
                self._author_count += 1
                print("finish scrapping author with id " + author_id)
                self._current_author = author_info
                time.sleep(3)