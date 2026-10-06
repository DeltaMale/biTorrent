import os
import tempfile

from flask import Flask, redirect, url_for, render_template, request, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, func
from forms import NewCourseForm, MagnetForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from torf import Torrent


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SECRET_KEY"] = "b4e56ytnbry456yurtjet7i"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///asd.db"
db.init_app(app)


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    magnets: Mapped[list["MagnetLink"]] = db.relationship(back_populates="uploader")


class MagnetLink(db.Model):
    __tablename__ = "magnet_link"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    magnet_uri: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    file_size: Mapped[str] = mapped_column(String(20), default="Unknown")
    uploader_id: Mapped[int] = mapped_column(
        Integer, db.ForeignKey("user.id"), nullable=False
    )
    uploader: Mapped["User"] = db.relationship(back_populates="magnets")
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    date_uploaded: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now()
    )


with app.app_context():
    db.create_all()


def login_required():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first.", "warning")
        return None
    return db.session.get(User, user_id)


def format_file_size(size):
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


@app.route("/")
@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/home_page")
def home_page():
    return redirect(url_for("home"))


@app.route("/downloads")
def download():
    search = request.args.get("q", "").strip()
    query = MagnetLink.query.order_by(MagnetLink.date_uploaded.desc())
    if search:
        query = query.filter(
            db.or_(
                MagnetLink.title.ilike(f"%{search}%"),
                MagnetLink.description.ilike(f"%{search}%"),
            )
        )
    magnets = query.all()
    return render_template("downloads.html", magnets=magnets, title="Downloads", search=search)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    user = login_required()
    if user is None:
        return redirect(url_for("login"))

    form = MagnetForm()
    if form.validate_on_submit():
        uploaded_file = form.file.data
        filename = secure_filename(uploaded_file.filename or "uploaded-file")

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, filename)
            uploaded_file.save(source_path)
            try:
                torrent = Torrent(source_path)
                torrent.generate()
                magnet_uri = str(torrent.magnet())
            except Exception:
                flash("The selected file could not be turned into a magnet link.", "danger")
                return render_template("upload.html", form=form, title="Share a Magnet")

            magnet = MagnetLink(
                title=form.title.data,
                magnet_uri=magnet_uri,
                description=form.description.data,
                file_size=format_file_size(os.path.getsize(source_path)),
                uploader_id=user.id,
            )
            db.session.add(magnet)
            db.session.commit()
        flash("Magnet link shared!", "success")
        return redirect(url_for("my_uploads"))

    return render_template("upload.html", form=form, title="Share a Magnet")


@app.route("/my-uploads")
def my_uploads():
    user = login_required()
    if user is None:
        return redirect(url_for("login"))
    magnets = (
        MagnetLink.query.filter_by(uploader_id=user.id)
        .order_by(MagnetLink.date_uploaded.desc())
        .all()
    )
    return render_template("my_uploads.html", magnets=magnets, title="My Uploads")


@app.route("/magnet/<int:magnet_id>")
def magnet_detail(magnet_id):
    user = login_required()
    if user is None:
        return redirect(url_for("login"))
    magnet = MagnetLink.query.get_or_404(magnet_id)
    return render_template("magnet_detail.html", magnet=magnet)


@app.route("/magnet/<int:magnet_id>/copy")
def magnet_copy(magnet_id):
    magnet = MagnetLink.query.get_or_404(magnet_id)
    magnet.download_count += 1
    db.session.commit()
    return render_template("magnet_copy.html", magnet=magnet)


@app.route("/magnet/<int:magnet_id>/delete", methods=["POST"])
def magnet_delete(magnet_id):
    user = login_required()
    if user is None:
        return redirect(url_for("login"))
    magnet = MagnetLink.query.get_or_404(magnet_id)
    if magnet.uploader_id != user.id:
        flash("Not your magnet to delete.", "danger")
        return redirect(url_for("my_uploads"))
    db.session.delete(magnet)
    db.session.commit()
    flash("Magnet deleted.", "info")
    return redirect(url_for("my_uploads"))


# ── Account ──


@app.route("/account")
def account():
    user = login_required()
    if user is None:
        return redirect(url_for("login"))
    count = MagnetLink.query.filter_by(uploader_id=user.id).count()
    total_downloads = (
        db.session.query(func.sum(MagnetLink.download_count))
        .filter(MagnetLink.uploader_id == user.id)
        .scalar()
        or 0
    )
    return render_template(
        "account.html", user=user, magnet_count=count, total_downloads=total_downloads
    )


# ── Auth ──


@app.route("/register", methods=["GET", "POST"])
def register():
    form = NewCourseForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        flash("Registered! Welcome aboard.", "success")
        return redirect(url_for("account"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Logged in.", "success")
            return redirect(url_for("account"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", title="Log In")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
