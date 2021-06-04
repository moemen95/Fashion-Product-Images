import os
import pandas as pd
from pandas import DataFrame

from tqdm import tqdm

from sqlalchemy import create_engine

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor_cext import CMySQLCursor

HOST = "localhost"
USER = "moemen"
PASSWORD = "moemen"
DATABASE_NAME = "fashion"
TABLE_NAME = "meta_data"
DATA_CSV = "../raw/raw_small/styles.csv"
IMAGES_CSV = "../raw/fashion-dataset/images.csv"
LOW_RES_DATA = "/home/moemen/Projects/IntuitionMachines/Fashion-Product-Images/raw/raw_small/images/"
HI_RES_DATA = "/home/moemen/Projects/IntuitionMachines/Fashion-Product-Images/raw/fashion-dataset/images/"


def connect_to_database_engine(host, user, password) -> (MySQLConnection, CMySQLCursor):
    """
    Connect to database engine
    :param host: the host of the database engine
    :param user: the user which we will use to access the database
    :param password: the password of the user
    :return: return cursor to the database
    """
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    return mydb, mydb.cursor()


def drop_database(db_cursor, database_name) -> None:
    db_cursor.execute("DROP DATABASE {}".format(database_name))
    db_cursor.execute("SHOW DATABASES")
    # see if it is created correctly or not
    for x in db_cursor:
        print(x)
    print("########################################")


def create_database(db_cursor, database_name) -> None:
    db_cursor.execute("CREATE DATABASE {}".format(database_name))
    db_cursor.execute("SHOW DATABASES")
    # see if it is created correctly or not
    for x in db_cursor:
        print(x)
    print("########################################")


def load_data() -> DataFrame:
    """
    Load the data from the csv files to pandas dataframe
    This function also will load the 3 More columns
    Low res image path
    Hi res image path
    Asset link
    :return: dataframe pandas ready to be used to deploy in mysql
    """
    # load the dataframe from styles.csv (Metadata)
    # Skip bad lines which has more than 10 columns
    # Get the header from the first line in the csv
    print("Reading CSV files")
    df = pd.read_csv(DATA_CSV, delimiter=",", header=0, error_bad_lines=False)
    df_images = pd.read_csv(IMAGES_CSV, delimiter=",", header=0, index_col="filename")

    # Get the path of the image based on it's id and check existence if not return None
    def get_path_of_image(__id, data_folder):
        img_path = data_folder + str(__id) + ".jpg"
        if os.path.isfile(img_path):
            return img_path
        else:
            return None

    # Get the asset link of the image based on it's id
    def get_asset_link_of_image(__id):
        img_name = str(__id) + ".jpg"
        try:
            return df_images.loc[img_name]["link"]
        except KeyError:
            return None

    print("Processing the dataframes")
    # Add column which contains the low res images paths in the local drive
    df["low_res_image_path"] = df.apply(lambda row: get_path_of_image(row["id"], LOW_RES_DATA), axis=1)

    # Add column which contains the hi res images paths in the local drive
    df["hi_res_image_path"] = df.apply(lambda row: get_path_of_image(row["id"], HI_RES_DATA), axis=1)

    # Add column which contains the asset link on the internet
    df["asset_link"] = df.apply(lambda row: get_asset_link_of_image(row["id"]), axis=1)

    # drop all nan rows
    df.dropna(inplace=True)

    print("Columns: ", df.columns)
    print("Count: {} rows".format(len(df.index)))

    # make id is the index
    df.set_index("id", inplace=True)
    print(df)
    print("Dataframes finished processing")
    return df


def main():
    # Connect to the database engine
    db, db_cursor = connect_to_database_engine(HOST, USER, PASSWORD)
    print("Connected to the database")

    # Drop database if found
    drop_database(db_cursor, DATABASE_NAME)
    print("Dropped the database")

    # Create database
    create_database(db_cursor, DATABASE_NAME)
    print("Created the database")

    db_cursor.close()
    print("Close the connection with the database")

    # Load the data into a pandas dataframe
    df = load_data()
    print("Dataframe is ready to populate")

    # AND Here is the magic BUDDY ! - Populate the dataframe to mysql database
    # Don't reinvent the wheel man
    engine = create_engine("mysql+mysqlconnector://moemen:moemen@localhost:3306/fashion")
    df.to_sql(TABLE_NAME, engine, if_exists='replace', index=True, index_label=None)
    print("Database now is ready and Done")


if __name__ == "__main__":
    main()
