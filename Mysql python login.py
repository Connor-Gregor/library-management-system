import mysql.connector



db = mysql.connector.connect(
    host='localhost',#change it to your own host
    user = "root", #change it to your own username 
    password = "password", #password for mysql database, change it to your own passowrd
    database = "person" #database name for login information
)

mycursor = db.cursor(buffered=True)

#For testing, local input
username = input("Enter Username: ")

mycursor.execute("SELECT username from person where username = %s", (username,)) #check if username exists in database
if mycursor.fetchone():
    password = input("Enter password: ")
    mycursor.execute("SELECT password FROM person WHERE username = %s AND password = %s", (username, password))
    if mycursor.fetchone():
        print("Login successful!")  
    else:print("Incorrect password")

else: print("Username not found")

