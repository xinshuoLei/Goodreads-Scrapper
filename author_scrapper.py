import requests
import bs4
import time

''' This file contains scrapper for authors
'''
class AuthorScrapper:
    
    def __init__(self, author_url, id):
        """ initialize a author scrapper

        Args:
            author_url: url of the author page
            id: author id
        """
        self._author_url = author_url
        # url of goodreads.com
        self._GOODREADS_URL = "https://goodreads.com"
        # info is the dictionary containing all info
        self._info = {}
        self._info["author_url"] = author_url
        self._info["_id"] = id
        self.request_url()


    def request_url(self):
        ''' use request to download html

        '''
        response = requests.get(self._author_url)
        if response:
            self._soup = bs4.BeautifulSoup(response.text, "html.parser")
            self.get_general_info()
            self.get_rating_info()
            self.get_author_books()
            self.get_related_authors()
            


    def get_author_books(self):
        ''' get all books by the author
        '''
        books_url = []
        actionLinks = self._soup.find_all("a", class_="actionLink", 
        style="float: right")
        for one_actionLink in actionLinks:
            if ("More books" in one_actionLink.get_text()):
                more_book_url = one_actionLink["href"]
        more_book_url = self._GOODREADS_URL + more_book_url

        response = None
        # check if there is a more books link
        if more_book_url:
            response = requests.get(more_book_url)
        books_soup = bs4.BeautifulSoup(response.text, "html.parser")
        
        # get urls on first page
        self.get_books_in_a_page(books_soup, books_url)
        # get urls on next page if there is a next page
        while (books_soup.find("a", class_ = "next_page") != None):
            # get url of next page
            next = books_soup.find("a", class_ = "next_page")
            next_response = requests.get(self._GOODREADS_URL + next["href"])
            if next_response:
                next_soup = bs4.BeautifulSoup(next_response.text, "html.parser")
                # avoid scrapping data too fasy
                time.sleep(5)
                self.get_books_in_a_page(next_soup, books_url)
                books_soup = next_soup
        
        self._info["author_books"] = books_url

    
    def get_books_in_a_page(self, page_soup, books_url):
        '''helper function for get_author_books. get all book urls in a page

        Args:
            soup for current page
            books_url: list to add urls to
        '''
        books_url_table = page_soup.find_all("a", {"class":"bookTitle", "itemprop":"url"})
        for url in books_url_table:
            books_url.append(self._GOODREADS_URL + url["href"])


    def get_related_authors(self):
        ''' get url of author page for all related authors
        '''
        urls = []

        # find link to page for related authors
        hreviews = self._soup.find("div", class_="hreview-aggregate").find_all("a")
        related_authors_url = None
        for one_hreview in hreviews:
            if one_hreview.get_text() == "Similar authors":
                related_authors_url = self._GOODREADS_URL + one_hreview["href"]

        response = requests.get(related_authors_url)
        if response:
            related_authors_soup = bs4.BeautifulSoup(response.text, "html.parser")
            authors_list = related_authors_soup.find_all("div", class_="listWithDividers")
            
            for one_list in authors_list:
                all_url = one_list.find_all("a", itemprop="url")
                for one_url in all_url:
                    # check to make sure the url is not a book page
                    if "book" not in one_url["href"] and "show" not in one_url["href"]:
                        append_url = one_url["href"].replace("list", "show")
                        urls.append(append_url)

        self._info["related_authors"] = urls[1:]

            

    def get_general_info(self):
        ''' get general info, including author name, review count, image_url
        '''
        soup = self._soup
        # author name
        self._info["name"] = soup.find("span", itemprop="name").get_text()
        # review count
        self._info["review_count"] = soup.find("span", class_="value-title", 
            itemprop="reviewCount")["content"]
        # image url get
        self._info["image_url"] = soup.find("img", alt=self._info["name"], 
            itemprop="image")["src"]


    def get_rating_info(self):
        ''' get rating info, including rating and rating count
        '''
        self._info["rating"] = self._soup.find("span", class_="average", 
            itemprop="ratingValue").get_text()
        self._info["rating_count"] = self._soup.find("span", 
            itemprop="ratingCount")["content"]

    def get_info_dictionary(self):
        ''' return a dictionary containing all info. used for inserting data
        '''
        return self._info
    


