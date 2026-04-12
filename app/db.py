import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_mysql_password",
        database="library_model"
    )

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT user_id, email, password, role
        FROM users
        WHERE email = %s
    """
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user