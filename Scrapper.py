import BookScrapper
from BookScrapper import *
from AuthorScrapper import *
import database


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
        book_id = self.find_id_in_url(strating_url)
        book = BookScrapper(strating_url, book_id)
        book_info = book.get_info_dictionary()
        database.insert_data(False, book_info)
        print("done")
        author_id = self.find_id_in_url(book_info["author_url"])
        print(author_id)
        author = AuthorScrapper(book_info["author_url"], author_id)
        database.insert_data(True, author.get_info_dictionary())
        
        
        
        
        
    def find_id_in_url(self, url):
        ''' find id of a book or author from url

        Return:
            id found
        '''
        print(url)
        everything_after_show = url.split("show/")[1]
        id = everything_after_show.split(".")[0]
        if (len(id) == len(everything_after_show)):
            # if split does not have any effect, the url is formatted in another way
            id = everything_after_show.split("-")[0]

        return id