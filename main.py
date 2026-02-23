from flask import Flask, redirect, url_for, render_template, request
from data import downloads, uploads, accounts


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/home_page")
def home_page():
    return redirect(url_for("home"))


@app.route("/account")
def account():
    return render_template("index.html", title="Account")


@app.route("/downloads")
def download():
    return render_template(
        "downloads_table.html", downloads=downloads, title="Downloads"
    )


@app.route("/uploads")
def upload():
    return render_template("uploads_table.html", uploads=uploads, title="Uploads")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        accounts.append({"username" : username, "password" : password})
        return redirect(url_for("home"))
    return render_template("register.html", title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html", title="Log In")


if __name__ == "__main__":
    app.run(debug=True)
