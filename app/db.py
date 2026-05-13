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
        password="admin", #password for mysql database, change it to your own passowrd
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
    cursor = conn.cursor()

    try:
        result_args = cursor.callproc('BorrowBook', (user_id, book_id, 0, ''))
        conn.commit()
        success = bool(result_args[2])
        message = result_args[3]
        
        return success, message

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

def get_all_borrowing_records(status_filter='all', sort_by='latest_borrow'):
    query = """
        SELECT h.borrow_id, p.username, b.title, h.borrow_date, h.due_date, h.return_date
        FROM borrowing_history h
        JOIN person p ON h.user_id = p.library_id
        JOIN book_collection b ON h.book_id = b.book_id
    """
    
    if status_filter == 'active':
        query += " WHERE h.return_date IS NULL"
    elif status_filter == 'returned':
        query += " WHERE h.return_date IS NOT NULL"
        
    if sort_by == 'earliest_due':
        query += " ORDER BY h.due_date ASC"
    elif sort_by == 'latest_due':
        query += " ORDER BY h.due_date DESC"
    elif sort_by == 'oldest_borrow':
        query += " ORDER BY h.borrow_date ASC"
    else:
        query += " ORDER BY h.borrow_date DESC"

    return query_db(query)

def get_all_books():
    query = """
        SELECT b.*, 
               EXISTS(SELECT 1 FROM borrowing_history h WHERE h.book_id = b.book_id) as has_history
        FROM book_collection b
    """
    return query_db(query)

def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM book_collection WHERE book_id = %s"
        cursor.execute(query, (book_id,))
        conn.commit()
        return True, "Book deleted successfully!"
    except mysql.connector.errors.IntegrityError:
        return False, "Cannot delete this book because it has active or past borrowing records. Please edit the book instead."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        cursor.close()
        conn.close()
        
def get_book_by_id(book_id):
    query = "SELECT * FROM book_collection WHERE book_id = %s"
    return query_db(query, (book_id,), fetchone=True)

def update_book(book_id, title, author_first, author_last, p_year, p_month, genre, copies):
    query = """
        UPDATE book_collection
        SET title = %s, author_first_name = %s, author_last_name = %s, 
            publish_year = %s, publish_month = %s, genre = %s, copies_available = %s
        WHERE book_id = %s
    """
    return query_db(query, (title, author_first, author_last, p_year, p_month, genre, copies, book_id))

def get_all_users():
    query = """
        SELECT library_id, username, email, first_name, last_name, role, address, city, zip_code
        FROM person 
        ORDER BY role ASC, last_name ASC
    """
    return query_db(query)

def get_user_by_id(user_id):
    query = "SELECT library_id, username, email, first_name, last_name, role, address, city, zip_code FROM person WHERE library_id = %s"
    return query_db(query, (user_id,), fetchone=True)

def update_user(user_id, username, email, first_name, last_name, address, city, zip_code, role):
    query = """
        UPDATE person
        SET username = %s, 
            email = %s, 
            first_name = %s, 
            last_name = %s, 
            address = %s, 
            city = %s, 
            zip_code = %s, 
            role = %s
        WHERE library_id = %s
    """
    return query_db(query, (username, email, first_name, last_name, address, city, zip_code, role, user_id))

def delete_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM person WHERE library_id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        return True, "User deleted successfully!"
    except mysql.connector.errors.IntegrityError:
        return False, "Can't remove user because they have borrowing logs"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        cursor.close()
        conn.close()

