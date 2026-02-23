from flask import Flask, redirect, url_for, render_template, request
from data import downloads, uploads, accounts
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///asd.db"
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]


with app.app_context():
    db.create_all()


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
        accounts.append({"username": username, "password": password})
        return redirect(url_for("home"))
    return render_template("register.html", title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html", title="Log In")


if __name__ == "__main__":
    app.run(debug=True)
