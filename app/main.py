from flask import Flask, render_template, request, redirect, url_for, session
from db import get_user_by_username

app = Flask(__name__)
app.secret_key = "simple-key"


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = get_user_by_username(username)

        if user is None:
            error = "Invalid username or password."
        elif user["pword"] != password:
            error = "Invalid username or password."
        else:
            session["user_id"] = user["library_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))

    return render_template("login.html", error=error)


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


if __name__ == "__main__":
    app.run(debug=True)