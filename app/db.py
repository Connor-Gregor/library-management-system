import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="PUT YOUR MYSQL WORKBENCH PASSWORD HERE", #password for mysql database, change it to your own passowrd
        database="Library_Model" #database name for login information
    )


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT library_id, username, pword, role
        FROM person
        WHERE username = %s
    """
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user