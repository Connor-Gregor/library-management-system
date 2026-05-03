import mysql.connector

# Helper function for easily using queries
def query_db(query, params=None, fetchone=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(query, params or ())

    if fetchone:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return result

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="PUT YOUR MYSQL WORKBENCH PASSWORD HERE", #password for mysql database, change it to your own passowrd
        database="Library_Model" #database name for login information
    )


def get_user_by_username(username):
    query = "SELECT library_id, username, pword, role FROM person WHERE username = %s"
    return query_db(query, (username,), fetchone=True)

def search_books(search_term):
    query = "SELECT book_id, title, author_first_name, author_last_name, genre, is_available FROM book_collection WHERE title LIKE %s OR author_first_name LIKE %s OR author_last_name LIKE %s OR genre LIKE %s"
    search_pattern = f"%{search_term}%"
    return query_db(query, (search_pattern, search_pattern, search_pattern, search_pattern))

def create_user(username, password, email, first_name, last_name, role='user'):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO person (username, pword, email, first_name, last_name, role)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (username, password, email, first_name, last_name, role))
    conn.commit()
    cursor.close()
    conn.close()

#fix this
def get_book(title, author_first_name, author_last_name):
    query = """
        SELECT book_id, title, author_first_name, author_last_name
        FROM book_collection
        WHERE title = %s
          AND author_first_name = %s
          AND author_last_name = %s
    """
    return query_db(query, (title, author_first_name, author_last_name), fetchone=True)

def create_book(title, author_first_name, author_last_name, publish_year, publish_month, genre, is_available):
    query = """
        INSERT INTO book_collection 
        (title, author_first_name, author_last_name, publish_year, publish_month, genre, is_available)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return query_db(query, (title, author_first_name, author_last_name, publish_year, publish_month, genre, is_available))