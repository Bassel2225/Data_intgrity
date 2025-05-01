import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_error
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Choose SQLite or MySQL as needed
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=3)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Allow insecure OAuth for localhost
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# GitHub OAuth
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    scope=["read:user", "user:email"]
)


app.register_blueprint(github_bp, url_prefix="/login")


# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    github_id = db.Column(db.String(100), unique=True)
    auth_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


with app.app_context():
    db.create_all()


# OAuth error handler
@oauth_error.connect_via(github_bp)
def github_error(blueprint, message, response):
    flash("GitHub OAuth error: " + message, "danger")
    return redirect(url_for("login"))


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not validate_password(password):
            flash("Password must be 8+ chars with uppercase, lowercase, number, and special char.", "warning")
            return redirect(url_for("signup"))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("signup"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password_hash=hashed_pw, auth_method="manual")
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = "remember" in request.form

        user = User.query.filter_by(email=email, auth_method="manual").first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session.permanent = remember
        log_login(user.id)
        flash("Login successful!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/login/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))

    resp = github.get("/user")
    if not resp.ok:
        flash("GitHub login failed.", "danger")
        print("GitHub API error:", resp.text)
        return redirect(url_for("login"))

    github_data = resp.json()
    print("GitHub user data:", github_data)

    github_id = str(github_data["id"])
    user = User.query.filter_by(github_id=github_id).first()

    if not user:
        email = github_data.get("email")
        if not email:
            # GitHub email may be private; fetch from /emails endpoint
            email_resp = github.get("/user/emails")
            if email_resp.ok:
                emails = email_resp.json()
                primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                email = primary_email or f"{github_data['login']}@github.com"
            else:
                email = f"{github_data['login']}@github.com"

        user = User(
            username=github_data["login"],
            email=email,
            github_id=github_id,
            auth_method="github"
        )
        try:
            db.session.add(user)
            db.session.commit()
            print("New GitHub user created.")
        except Exception as e:
            db.session.rollback()
            print("Database error:", e)
            flash("Database error while saving GitHub user.", "danger")
            return redirect(url_for("login"))

    session["user_id"] = user.id
    session.permanent = True
    log_login(user.id)
    print("GitHub login successful, session:", session)
    flash("Logged in with GitHub!", "success")
    return redirect(url_for("profile"))


@app.route("/profile")
def profile():
    user = get_logged_in_user()
    if not user:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    return render_template("profile.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


def get_logged_in_user():
    uid = session.get("user_id")
    if uid:
        return User.query.get(uid)
    return None


def log_login(user_id):
    ip = request.remote_addr
    log = LoginLog(user_id=user_id, ip_address=ip)
    db.session.add(log)
    db.session.commit()


def validate_password(password):
    import re
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
