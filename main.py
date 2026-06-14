from flask import Flask, redirect, url_for, render_template, request, flash, session
from data import downloads, uploads, accounts
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from forms import NewCourseForm


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SECRET_KEY"] = "b4e56ytnbry456yurtjet7i"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:////home/alseczb/Documents/Code/biTorrent/asd.db"
)
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(32), nullable=False)


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
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    user = User.query.get(user_id)
    return render_template("account.html", user=user)


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
    form = NewCourseForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                password=form.password.data,
            )
            if User.query.filter_by(username=user.username).first():
                flash(
                    "Username already exists. Please choose a different one.", "danger"
                )
                return redirect(url_for("register"))
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("You are now registered!", "success")
            return redirect(url_for("account"))
    return render_template(
        "register.html",
        title="Register",
        form=form,
        username=form.username.data,
        password=form.password.data,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("account"))
        flash("Invalid login", "danger")
    return render_template("login.html", title="Log In")


if __name__ == "__main__":
    app.run(debug=True)
