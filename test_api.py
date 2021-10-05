from api import *
import unittest
import json

'''
This file contains all unit test for this assignment
'''

class ApiTest(unittest.TestCase):
    def test_get_id(self):
        resp = app.test_client().get("/author?id=18")
        self.assertEqual(200, resp.status_code)
        with open("author get.json", "w") as file:
            file.write(resp.get_json())
    
    def test_get_nonexistent_id(self):
        resp = app.test_client().get("/author?id=222")
        dict = json.loads(resp.get_json())
        self.assertEqual(200, resp.status_code)
        # error should be reported
        self.assertTrue("error" in dict.keys())
    
    def test_search_valid_query(self):
        resp = app.test_client().get("/search?q=book.rating:>4.5")
        self.assertEqual(200, resp.status_code)
        with open("author search.json", "w") as file:
            file.write(resp.get_json())

    def test_search_invalid_query(self):
        resp = app.test_client().get("/search?q=book.rating AND")
        self.assertEqual(200, resp.status_code)
        dict = json.loads(resp.get_json())
        # error should be reported
        self.assertTrue("error" in dict.keys())
    

    def test_delete_invalid(self):
        resp = app.test_client().delete("/book?id=24374")
        self.assertEqual(200, resp.status_code)
        dict = json.loads(resp.get_json())
        # error should be reported
        self.assertTrue("error" in dict.keys())
    

    def test_invalid_scrap(self):
        # this shoud fail because this author alreay exist in database
        resp = app.test_client().post("/scrape?attr=https://www.goodreads."
        +"com/author/show/811.Yann_Martel")   
        self.assertEqual(200, resp.status_code)
        dict = json.loads(resp.get_json())
        # error should be reported
        self.assertTrue("error" in dict.keys())
    
    
    def test_post_blank(self):
        data_dic = {}
        # test with blank body, status code should be 400
        resp = app.test_client().post("/author", data=json.dumps(data_dic), 
            content_type='application/json')
        self.assertEqual(400, resp.status_code)

    def test_post_wrong_type(self):
        data_dic = {"_id": 12345}
        # test with wrong content type, status code should be 415
        resp = app.test_client().post("/author", data=json.dumps(data_dic), 
            content_type='application/')
        self.assertEqual(415, resp.status_code)

    def test_post_and_get(self):
        data_dic = {"_id": "123456",
                    "author_url": "https://www.goodreads.com/",
                    "name": "Fake Author1",
                    "review_count": "35000",
                    "image_url": "https://goodreads.com",
                    "rating": "3.5",
                    "rating_count": "50000",
                    "author_books": [
                    ],
                    "related_authors": [
                    ]}
        # post and then get
        resp_post = app.test_client().post("/author", data=json.dumps(data_dic), 
            content_type='application/json')
        self.assertEqual(200, resp_post.status_code)
        resp_get = app.test_client().get("/author?id=123456")
        self.assertEqual(200, resp_post.status_code)
        with open("post and get.json", "w") as file:
            file.write(resp_get.get_json())
        # delete in the end so unit test can be reused
        app.test_client().delete("/author?id=123456")

    def test_update_and_get(self):
        update = {"rating_count": "50000"}
        # id=1234567 is a fake book I created
        resp = app.test_client().put("/book?id=1234567", data=json.dumps(update), 
            content_type='application/json')
        self.assertEqual(200, resp.status_code)
        # make a geat request
        resp_get = app.test_client().get("/book?id=1234567")
        self.assertEqual(200, resp_get.status_code)
        # check value is updated
        dic = loads(resp_get.get_json())
        for one_elem in dic:
            self.assertEqual(update["rating_count"], one_elem["rating_count"])
        with open("update and get.json", "w") as file:
            file.write(resp_get.get_json())
    
if __name__ == "__main__":
    unittest.main()
