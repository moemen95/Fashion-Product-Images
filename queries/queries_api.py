from typing import List, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def connect_to_fashion_database(user, password, host, database_name) -> Engine:
    """
    Connect to mysql database with port assumption 3306
    :param user: user of mysql
    :param password: password of mysql
    :param host: host of mysql
    :param database_name: the name of the database
    :return: engine
    """
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:3306/{}".format(user, password, host, database_name))
    return engine


def fetch_query_from_meta_data(engine, select, where_dict, order_by='year') -> List[Dict]:
    """
    Simple API to query fetch from fashion database meta_data table and a little bit more generic usage
    :param engine: the engine to connect to our database
    :param select: the columns you wanna return
    :param where_dict: the dictionary of the conditions you wanna fetch
        Example:
        where_dict={
                        "gender": ["=", "Men"],
                        "subCategory": ["=", "shoes"],
                        "year": [">", "2012"],
                    }
        Key is the column name
        Value is list of 2 items [Operator,Value]
    :param order_by: order by one column name and if not set the year column will be used instead
    :return: list of results
    """
    # Construction of the where statement
    where_statement = []
    for key, val in where_dict.items():
        operator, value = val
        where_statement.append("`{}`{}'{}'".format(key, operator, value))
    # Join and between them
    where_statement = " AND ".join(where_statement)
    # Constructing the fetch query
    fetch_query = """SELECT t.*
FROM fashion.meta_data t
WHERE {}
ORDER BY {}
""".format(where_statement, order_by)
    print("Check here the query: ")
    print(fetch_query)

    ret = []  # The return list of dicts

    # connect and execute the query
    with engine.connect() as conn:
        result = conn.execute(text(fetch_query))
        # construct the list which i will return
        for row in result:
            # Append the dict of every select key with it's value
            ret.append(dict((select_key, row[select_key]) for select_key in select))  # Hmmm too Complicated ! xDxD
    return ret


def test():
    engine = connect_to_fashion_database("moemen",
                                         "moemen",
                                         "localhost",
                                         "fashion")
    res = fetch_query_from_meta_data(engine=engine,
                                     select=["hi_res_image_path", "asset_link"],
                                     where_dict={
                                         "gender": ["=", "Men"],
                                         "subCategory": ["=", "shoes"],
                                         "year": [">", "2012"],
                                     })
    print(res)


if __name__ == '__main__':
    test()
