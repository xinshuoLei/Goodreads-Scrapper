import re

AUTHOR_ATTRIBUTES = ["_id", "author_url", "name", "review_count", "image_url", "rating", 
    "rating_count", "author_books", "related_authors"]
NUMBER_ATTRIBUTES = ["id", "review_count", "rating", "rating_count"]
BOOK_ATTRIBUTES = ["id", "book_url", "rating", "rating_count", "author", "author_url",
    "title", "ISBN", "review_count", "image_url", "similar_books"]
ATTRIBUTES = {"author": AUTHOR_ATTRIBUTES, "book": BOOK_ATTRIBUTES}


def parse_whole_argument(query):
    ''' function that deal with whole query containing logic operator

    Args:
        query: query to parse

    Return:
        (condition for the find() function in database, table). None for invalid query
    '''
    and_result = re.search("AND", query)
    or_result = re.search("OR", query)
    not_result = re.search("NOT", query)
    if and_result:
        # if nothing before AND or nothing after AND, then invalid
        if and_result.span()[0] == 0 or and_result.span()[1] == len(query):
            print("invalid AND query")
        return parse_and(query)
        
    elif or_result:
        # if nothing before OR or nothing after OR, then invalid
        if or_result.span()[0] == 0 or or_result.span()[1] == len(query):
            print("invalid OR query")

        
    elif not_result:
        removed_not_query = query.replace("NOT", "", 1)
        return parse_single_query(removed_not_query, True)
    else:
        return parse_single_query(query, False)
    
    return None

def parse_single_query(query, contain_not):
    ''' function that parse a single query, i.e. does not contain any logic operator
    
    Args:
        query: the query to parse
        contain_not: true if the original_query contain NOT 
                    (NOT is removed in parse_whole_argument())

    Return: (condition for the find() function in database, table). None for invalid query
    '''
    if check_logic_operator(query):
        print("invalid query. Nested/chained operator are not supported.")
        return None
    
    dot_result = re.search(r"\.", query)
    colon_result = re.search(r"\:", query)

    # the query is invalid if no attribute is specified
    if dot_result is None or dot_result.span()[0] == 0 or dot_result.span()[1] == len(query):
        return None

    table = re.split(r"\.", query)[0]
    if colon_result is None:
        # output all values for the attribute if query only contains "."
        attribute = re.split(r"\.", query)[1]
        if table not in ATTRIBUTES or attribute not in ATTRIBUTES[table]:
            print("table or attribute does not exist")
            return None
        return ({}, {"_id":0, attribute: 1}, table)
    else:
        # attribute is the string between "." and ":"
        attribute = re.search(r".\.(.*?)\:", query).group(1)
        # if table is not book or author or attribute does not exist, invalid
        
        if table not in ATTRIBUTES or attribute not in ATTRIBUTES[table]:
            print("table or attribute does not exist")
            return None
        
        # check for > or <
        greater_than_result = re.search(">", query)
        less_than_result = re.search("<", query)
        quote_result = re.search(r"\"", query)

        if greater_than_result:
            value = is_query_valid(query, ">", attribute)
            if value:
                if contain_not: 
                    return ({"$expr": {"$not": {"$gt": 
                        [{ "$toDouble": "$"+ attribute}, value]}}}, table)
                return ({"$expr": {"$gt": 
                    [{ "$toDouble": "$"+ attribute}, value]}}, table)
        
        elif less_than_result:
            value = is_query_valid(query, "<", attribute)
            if value:
                if contain_not:
                    return ({"$expr": {"$not": {"$lt": 
                        [{ "$toDouble": "$"+ attribute}, value]}}}, table)
                return ({"$expr": {"$lt":
                    [{ "$toDouble": "$"+ attribute}, value]}}, table)

        elif quote_result:
            # check there are only two quotes if quotes exist
            if len(re.findall(r"\"", query)) != 2:
                print("invalid number of quotes")
                return None
            value = is_query_valid(query, "\"", attribute)
            if value:
                if contain_not:
                    return ({attribute: {"$ne": value}}, table)
                return ({attribute: value}, table)
        
        else:
            # only colon operator, search for attributes containing value
            value = is_query_valid(query, r"\:", attribute)
            if value:
                if contain_not:
                    return ({attribute: {"$not": {"$regex": value, "$options": "i" }}}, table)
                return ({attribute: {"$regex": value, "$options": "i" }}, table)

    return None

def parse_and(query):
    ''' function that deal with whole query containing AND

    Args:
        query: query to parse

    Return:
        (condition for the find() function in database, table). None for invalid query
    '''
    queries = query.split("AND")
    first_query_result = parse_single_query(queries[0].strip(), False)
    second_query_result = parse_single_query(queries[1].strip(), False)

    if first_query_result and second_query_result:
        if first_query_result[-1] == second_query_result[-1]:
            return ({"$and": [first_query_result[0], second_query_result[0]]},
                    first_query_result[-1])

    print("queries separated by AND are not on the same table")
    return None


def parse_or(query):
    ''' function that deal with whole query containing OR

    Args:
        query: query to parse

    Return:
        (condition for the find() function in database, table). None for invalid query
    '''
    queries = query.split("OR")
    first_query_result = parse_single_query(queries[0].strip(), False)
    second_query_result = parse_single_query(queries[1].strip(), False)

    if first_query_result and second_query_result:
        if first_query_result[-1] == second_query_result[-1]:
            return ({"$or": [first_query_result[0], second_query_result[0]]},
                first_query_result[-1])

    print("queries separated by OR are not on the same table")
    return None


def check_logic_operator(query):
    ''' check if there is a logic operator in query

    Args:
        query: query to check
    
    Return:
        true if query contain logic operator. false otherwise
    '''
    and_result = re.search("AND", query)
    or_result = re.search("OR", query)
    not_result = re.search("NOT", query)
    if and_result or or_result or not_result:
        return True
    return False

def is_query_valid(query, operator, attribute):
    if operator == ">" or operator == "<":
        if attribute not in NUMBER_ATTRIBUTES:
            print("non numerical values are not comparable")
            return None
    value = re.split(operator, query)[1].strip()
    if len(value) != 0:
        value_is_numerical = value.replace(".", "", 1).isdigit()
        if attribute in NUMBER_ATTRIBUTES and value_is_numerical:
            return float(value)
        else:
            print("specified value is not the corect type")
    return None

    