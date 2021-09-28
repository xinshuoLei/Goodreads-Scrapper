import requests
import bs4

''' This file contains scrapper for the book
'''
class BookScrapper():

    def __init__(self, book_url, id):
        """ initialize a author scrapper

        Args:
            book_url: url of the book page
            id: book id
        """
        self._book_url = book_url
        # url of goodreads.com
        self._GOODREADS_URL = "https://goodreads.com"
        # info is the dictionary that stores all information
        self._info = {}
        self._info["book_url"] = book_url
        self._info["_id"] = id
        self.request_url()
    

    def request_url(self):
        ''' use request to download html

        '''
        response = requests.get(self._book_url)
        if response:
            self._soup = bs4.BeautifulSoup(response.text, "html.parser")
            # scrap infos
            self.get_rating_info()
            self.get_author_info()
            self.get_general_info()
            self.get_similar_books()

    
    def get_rating_info(self):
        ''' get rating info including rating and rating_count
        '''
        # get and remove blank spaces
        rating_component = self._soup.find("span", itemprop="ratingValue")
        self._info["rating"] = rating_component.get_text().strip()
        rating_count_component = self._soup.find("meta", itemprop="ratingCount")
        self._info["rating_count"] = rating_count_component["content"].strip()
        


    def get_general_info(self):
        '''  get general infos including title, ISBN, review count, url of book cover
        '''
        soup = self._soup
        
        # title
        title = soup.find("h1", id="bookTitle").get_text()
        # remove new line and white space
        self._info["title"] = title.replace("\n", "").strip()
        
        # ISBN
        book_data = soup.find("div", id="bookDataBox")
        clear_floats = book_data.find_all("div", class_ = "clearFloats")
        # iterate through all clearFloats class, find the one with title as ISBN
        for one in clear_floats:
            if one.find("div", class_ = "infoBoxRowTitle").get_text() == "ISBN":
                isbn_component = one.find("div", class_ = "infoBoxRowItem")
                # get text and remove blank spaces and newline
                self._info["ISBN"] = isbn_component.get_text().replace("\n", " ").replace(" ", "")

        # review count
        self._info["review_count"] = soup.find("meta", itemprop="reviewCount")["content"].strip()

        # url of cover image
        self._info["image_url"] = soup.find("img", id="coverImage")["src"]

        
    def get_author_info(self):
        ''' get author info including author name and url of author page
        '''
        soup = self._soup
        self._info["author"] = soup.find("span", itemprop="name").get_text()
        self._info["author_url"] = soup.find("a", {"class": "authorName", 
            "itemprop": "url"})["href"]

        
    def get_similar_books(self):
        '''get url of all similar books
        '''
        # url of the page that contains all similar books
        similar_books_page = self._soup.find("a", class_="actionLink right seeMoreLink")["href"]
        response = requests.get(similar_books_page)
        if response:
            similar_book_soup = bs4.BeautifulSoup(response.text, "html.parser")
            # find all listWidthDividers first
            similar_books_list = similar_book_soup.find_all("div", class_ = "listWithDividers")
            urls = []

            for one_list in similar_books_list:
                # all urls in one list
                all_url = one_list.find_all("a", itemprop = "url")
                for one_url in all_url:
                    # all urls contain both link to similar books and link to author
                    # of similar book. the difference is book page has a span with itemprop 
                    # as name, while author urls do not
                    if (one_url.find(("span"), itemprop = "name") != None):
                        urls.append(self._GOODREADS_URL + one_url["href"])
            
            # the first url is itself
            self._info["similar_books"] = urls[1:]

    
    def get_info_dictionary(self):
        ''' return a dictionary containing all info. used for inserting data
        '''
        return self._info






