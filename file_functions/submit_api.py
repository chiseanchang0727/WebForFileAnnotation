from sqlalchemy import text
from datetime import datetime
from mysql_connector import MySqlConnector
from dotenv import load_dotenv
import pandas as pd
import os
load_dotenv()


connector = MySqlConnector(
    host=os.getenv("MYSQL_HOST"),
    database=os.getenv("MYSQL_DATABASE"),
    userN=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD") 
)

def submit(file_name: str,author:str, page_num:str, description: str):
    """
    update into my dataframe in pandas and then upload to MySQL database
    """
   
    # df = pd.read_sql("data", connector.engine)
    # print(df)
    # Create a new row with the provided data
    new_row = {
        "file_name": file_name,
        "author": author,
        "page_num": page_num,
        "description": description,
        "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Append the new row to the DataFrame
    
    # df = pd.concat([df, pd.DataFrame(new_row)], axis=)
    df = pd.DataFrame([new_row])
    
    # Upload the updated DataFrame to MySQL
    df.to_sql("annotation_data", connector.engine, if_exists='append', index=False)
    return {"message": "Data submitted successfully", "annotation_data": new_row}



def file_upload(author:str,file_name: str, file: bytes):

    """
    add file as data bytes into my dataframe in pandas and then upload to MySQL source_file table
    """
   
    # df = pd.read_sql("data", connector.engine)
    # print(df)
    # Create a new row with the provided data
    new_row = {
        "file_name": file_name,
        "author": author,
        "file":file
    }
    
    # Append the new row to the DataFrame
    
    # df = pd.concat([df, pd.DataFrame(new_row)], axis=)
    df = pd.DataFrame([new_row])
    
    # Upload the updated DataFrame to MySQL
    df.to_sql("source_file", connector.engine, if_exists='append', index=False)
    return {"message": "Data submitted successfully", "source_file": new_row}


def GetFile(userN: str):
    """
    Return all file names associated with the given user.
    """
    query = """
    SELECT file_name
    FROM source_file
    WHERE author = :author
    """
    params = {"author": userN}
    df = pd.read_sql_query(text(query), connector.engine, params=params)
    return df.reset_index(drop=True)


def fetch_pdf_by_name(author: str, file_name: str):
    """
    Fetch the PDF file row(s) by author and name from the MySQL database.
    """
    query = """
    SELECT *
    FROM source_file
    WHERE author = :author AND file_name = :file_name
    LIMIT 1
    """
    params = {"author": author, "file_name": file_name}
    df = pd.read_sql_query(text(query), connector.engine, params=params)
    return df

def latestPage(author:str, file_name: str):
    """
    Fetch the latest page number for a given file name and author.
    """
    query = """
    SELECT MAX(page_num) as latest_page
    FROM annotation_data
    WHERE author = :author AND file_name = :file_name
    """

    params = {"author": author, "file_name": file_name}
    df = pd.read_sql_query(text(query), connector.engine, params=params)

    latest_page = df["latest_page"].iloc[0]
    
    if pd.isna(latest_page):
        latest_page = 1  # Default to page 1 if no records found
    else:
        latest_page = int(latest_page)  # Ensure it's an integer

    return latest_page
