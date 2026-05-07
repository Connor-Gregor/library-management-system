import mysql.connector
from datetime import date, timedelta

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
        password="YOUR MYSQL PASSWORD", #password for mysql database, change it to your own passowrd
        database="Library_Model" #database name for login information
    )


def get_user_by_username(username):
    query = "SELECT library_id, username, pword, role FROM person WHERE username = %s"
    return query_db(query, (username,), fetchone=True)

def search_books(search_term):
    query = "SELECT book_id, title, author_first_name, author_last_name, genre, copies_available FROM book_collection WHERE title LIKE %s OR author_first_name LIKE %s OR author_last_name LIKE %s OR genre LIKE %s"
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

def create_book(title, author_first_name, author_last_name, publish_year, publish_month, genre, copies_available):
    query = """
        INSERT INTO book_collection 
        (title, author_first_name, author_last_name, publish_year, publish_month, genre, copies_available)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    return query_db(query, (title, author_first_name, author_last_name, publish_year, publish_month, genre, copies_available))

def borrow_book(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM borrowing_history WHERE user_id = %s AND book_id = %s AND return_date IS NULL", (user_id, book_id))
        already_borrowed = cursor.fetchone()
        
        if already_borrowed:
            return False, "You already have a copy of this book checked out!"

        cursor.execute("SELECT copies_available FROM book_collection WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        
        if not book or book['copies_available'] < 1:
            return False, "Sorry, there are no copies of this book left."

        cursor.execute("UPDATE book_collection SET copies_available = copies_available - 1 WHERE book_id = %s", (book_id,))
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=30)
        insert_query = """
            INSERT INTO borrowing_history (user_id, book_id, borrow_date, due_date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, book_id, borrow_date, due_date))
        conn.commit()
        return True, "Book borrowed successfully! It is due in 30 days."

    except Exception as e:
        conn.rollback()
        return False, f"An error occurred: {str(e)}"
    finally:
        cursor.close()
        conn.close()
        
def return_book(user_id, book_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        update_history = """
            UPDATE borrowing_history 
            SET return_date = %s 
            WHERE user_id = %s AND book_id = %s AND return_date IS NULL
        """
        cursor.execute(update_history, (date.today(), user_id, book_id))
        update_book = "UPDATE book_collection SET copies_available = copies_available + 1 WHERE book_id = %s"
        cursor.execute(update_book, (book_id,))
        conn.commit()
        return True, "Book returned successfully! Thank you."

    except Exception as e:
        conn.rollback()
        return False, f"An error occurred: {str(e)}"
    finally:
        cursor.close()
        conn.close()
        
def get_my_borrowed_books(user_id):
    query = """
        SELECT b.book_id, b.title, b.author_first_name, b.author_last_name, bh.borrow_date, bh.due_date
        FROM book_collection b
        JOIN borrowing_history bh ON b.book_id = bh.book_id
        WHERE bh.user_id = %s AND bh.return_date IS NULL
    """
    return query_db(query, (user_id,))

def get_user_borrowing_history(user_id):
    query = """
        SELECT b.title, b.author_first_name, b.author_last_name, bh.borrow_date, bh.due_date, bh.return_date
        FROM book_collection b
        JOIN borrowing_history bh ON b.book_id = bh.book_id
        WHERE bh.user_id = %s
        ORDER BY bh.borrow_date DESC
    """
    return query_db(query, (user_id,))

def get_all_borrowing_records():
    query = """
        SELECT h.borrow_id, p.username, b.title, h.borrow_date, h.due_date, h.return_date
        FROM borrowing_history h
        JOIN person p ON h.user_id = p.library_id
        JOIN book_collection b ON h.book_id = b.book_id
        ORDER BY h.borrow_date DESC
    """
    return query_db(query)

def get_all_books():
    query = """
        SELECT book_id, title, author_first_name, author_last_name, publish_year
        FROM book_collection
        ORDER BY title
    """
    return query_db(query)

def delete_book(book_id):
    query = "DELETE FROM book_collection WHERE book_id = %s"
    return query_db(query, (book_id,))