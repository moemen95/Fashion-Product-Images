import json
from typing import List, Dict

import boto3
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from tqdm import tqdm
from helper_functions import timeit


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


@timeit
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

    print("Executing the query")
    # connect and execute the query
    with engine.connect() as conn:
        result = conn.execute(text(fetch_query))
        # construct the list which i will return
        for row in result:
            # Append the dict of every select key with it's value
            ret.append(dict((select_key, row[select_key]) for select_key in select))  # Hmmm too Complicated ! xDxD
    print("Query Done.")
    return ret


@timeit
def store_images_n_metadata_in_s3_bucket(bucket_name, cloud_root, rows: List[Dict], image_key) -> None:
    """
    Store images and their metadata in json called (meta-data.json)
    :param bucket_name: name of the aws bucket
    :param cloud_root: root folder in the aws bucket
    :param rows: List[Dict] contains the results of the queries
    :param image_key: the key of the image in the row of the query
    :return:
    """
    print("Uploading images to AWS S3 Bucket..")
    s3_client = boto3.client('s3')
    for row in tqdm(rows):
        filename = row[image_key]
        object_name = cloud_root + filename.split("/")[-1]
        response = s3_client.upload_file(filename, bucket_name, object_name)
    json_name = cloud_root + "meta-data.json"
    s3_resource = boto3.resource('s3')
    s3object = s3_resource.Object(bucket_name, json_name)
    s3object.put(Body=(bytes(json.dumps(rows).encode('UTF-8'))))


@timeit
def fetch_n_store(engine, select, where_dict, order_by, s3_bucket_name, cloud_root) -> None:
    """
    Fetch the query using fetch_query_from_meta_data
    Then Store the query results using store_images_n_metadata_in_S3_bucket
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
    :param s3_bucket_name: name of the aws bucket
    :param cloud_root: root folder in the aws bucket
    :return:
    """
    res = fetch_query_from_meta_data(engine=engine,
                                     select=select,
                                     where_dict=where_dict,
                                     order_by=order_by)
    print(res)
    store_images_n_metadata_in_s3_bucket(s3_bucket_name, cloud_root, res, "low_res_image_path")


def test():
    engine = connect_to_fashion_database("moemen",
                                         "moemen",
                                         "localhost",
                                         "fashion")
    fetch_n_store(engine=engine,
                  select=["id", "gender", "masterCategory", "subCategory", "articleType", "baseColour", "season",
                          "year", "usage", "productDisplayName", "low_res_image_path", "hi_res_image_path",
                          "asset_link"],
                  where_dict={
                      "gender": ["=", "Men"],
                      "subCategory": ["=", "shoes"],
                      "year": [">", "2012"],
                  },
                  order_by="year",
                  s3_bucket_name="moemenfashionbucket",
                  cloud_root="Men/shoes/>2012/")


if __name__ == '__main__':
    test()
