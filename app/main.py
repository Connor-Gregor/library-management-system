from flask import Flask, render_template, request, redirect, url_for, session
from db import get_user_by_email

app = Flask(__name__)
app.secret_key = "simple-key"

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        if user is None:
            error = "User not found."
        elif user["password"] != password:
            error = "Incorrect password."
        else:
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("user_dashboard"))

    return render_template("login.html", error=error)

@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/user")
def user_dashboard():
    return render_template("user_dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)