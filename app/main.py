from enum import nonmember
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import (get_user_by_username, create_user, search_books, get_book, create_book, borrow_book,
                get_my_borrowed_books, return_book, get_user_borrowing_history, get_all_borrowing_records,
                get_all_books, delete_book, get_book_by_id, update_book, get_all_users, get_user_by_id, delete_user_by_id,
                update_user)
from werkzeug.security import generate_password_hash, check_password_hash  

app = Flask(__name__)
app.secret_key = "simple-key"

failed_login_tracker = {}

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            error = "Please fill out all fields."
            return render_template("login.html", error=error)

        user = get_user_by_username(username)
        current_time = time.time()
        tracker = failed_login_tracker.get(username, {"attempts": 0, "lock_until": 0})
    
        if tracker["lock_until"] > current_time:
            error = "Too many failed attempts. Account locked for 1 minute."
            return render_template("login.html", error=error)

        if user is None:
            error = "Invalid username or password."
            return render_template("login.html", error=error)
       
        if "$" in user["pword"]:
            password_is_correct = check_password_hash(user["pword"], password)
        else:
            password_is_correct = (password == user["pword"])
      
        if not password_is_correct:
            error = "Invalid username or password."
            tracker["attempts"] += 1
            if tracker["attempts"] > 4:
                tracker["lock_until"] = current_time + 60
                error = "Too many failed attempts. Account locked for 1 minute."
            
            failed_login_tracker[username] = tracker
            return render_template("login.html", error=error)
            
        failed_login_tracker.pop(username, None)

        session["user_id"] = user["library_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("user_dashboard"))

    return render_template("login.html", error=error)
    

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        
        existing_user = get_user_by_username(username)
        if "@" not in email:
            error = "Invalid email address."
        elif existing_user:
            error = "That username is already taken. Please choose another."
        elif len(password) < 5:
            error = "Password must be at least 5 characters long."
        else:
            hashed_password = generate_password_hash(password)
            create_user(username, hashed_password, email, first_name, last_name)
            flash("Registration successful!", "success")
            return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("user_dashboard"))

    return render_template("admin_dashboard.html")


@app.route("/user")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("user_dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/user/books", methods=["GET", "POST"])
def user_books():
    if "user_id" not in session:
        return redirect(url_for("login"))

    books = []
    search_term = ""

    if request.method == "POST":
        search_term = request.form.get("search", "")
        books = search_books(search_term)

    return render_template("user_books.html", books=books, search_term=search_term)


@app.route("/admin/new_book", methods=["GET", "POST"])
def admin_add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return redirect(url_for("user_dashboard"))

    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        a_first_name = request.form.get("author_first_name", "").strip()
        a_last_name = request.form.get("author_last_name", "").strip()
        genre = request.form.get("genre", "").strip()

        if not title or not a_first_name or not a_last_name or not genre:
            error = "Title, author name, and genre are required."
            return render_template("add_book.html", error=error)

        try:
            p_year = int(request.form.get("publish_year"))
            p_month = int(request.form.get("publish_month"))
            copies_available = int(request.form.get("copies_available"))
        except ValueError:
            error = "Publish year, month, and copies must be numbers."
            return render_template("add_book.html", error=error)

        if p_month < 1 or p_month > 12:
            error = "Month must be between 1 and 12."
            return render_template("add_book.html", error=error)

        if p_year > 2026:
            error = "Invalid publish year."
            return render_template("add_book.html", error=error)

        if copies_available < 0:
            error = "Copies cannot be negative."
            return render_template("add_book.html", error=error)

        existing_book = get_book(title, a_first_name, a_last_name)

        if existing_book:
            error = "That book has already been added to the library."
        else:
            create_book(title, a_first_name, a_last_name, p_year, p_month, genre, copies_available)
            flash("Addition successful!", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template("add_book.html", error=error)


@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    success, message = borrow_book(user_id, book_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("user_books"))


@app.route("/my_books")
def my_books():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    active_books = get_my_borrowed_books(user_id)
    history_books = get_user_borrowing_history(user_id)
    return render_template("my_books.html", active_books=active_books, history_books=history_books)


@app.route("/return/<int:book_id>", methods=["POST"])
def return_book_route(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    success, message = return_book(user_id, book_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("my_books"))


@app.route("/admin/history")
def admin_history():
    if session.get("role") != "admin":
        flash("Unauthorized access. Admins only.", "error")
        return redirect(url_for("login"))

    status_filter = request.args.get("status", "all")
    sort_by = request.args.get("sort", "latest_borrow")
    records = get_all_borrowing_records(status_filter, sort_by)
    return render_template("admin_history.html", records=records)

@app.route("/admin/view_books")
def admin_view_books():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    books = get_all_books()
    return render_template("admin_view_all_books.html", books=books)


@app.route("/admin/view_users")
def admin_view_users():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    users = get_all_users()
    return render_template("admin_view_all_users.html", users=users)


@app.route("/admin/user/edit/<int:user_id>", methods=["GET", "POST"])
def admin_edit_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    error = None
    user = get_user_by_id(user_id) 
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin_view_users"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        role = request.form.get("role", "").strip()
        
        if not username or not email or not first_name or not last_name or not role:
            error = "All fields are required."
            return render_template("edit_user.html", user=user, error=error)
        if "@" not in email:
            error = "Invalid email address format."
            return render_template("edit_user.html", user=user, error=error)
        if role not in ["user", "admin"]:
            error = "Invalid role tier assignment selection."
            return render_template("edit_user.html", user=user, error=error)
            
        update_user(user_id, username, email, first_name, last_name, role)
        flash("User info updated successfully!", "success")
        return redirect(url_for("admin_view_users"))

    return render_template("edit_user.html", user=user, error=error)


@app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    
    if user_id == session.get("user_id"):
        flash("Security Alert: System rules protect active administrators from self-deletion.", "error")
        return redirect(url_for("admin_dashboard"))

    delete_user_by_id(user_id)
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_view_users"))

if __name__ == "__main__":
    app.run(debug=True)