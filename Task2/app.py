import os
import re
import jwt
from datetime import timedelta, datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_error
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=3)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# JWT secret key (make sure to use a strong, secret key)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))  # optional
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

# Utility Functions
def validate_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def log_login(user_id):
    ip = request.remote_addr
    log = LoginLog(user_id=user_id, ip_address=ip)
    db.session.add(log)
    db.session.commit()

def get_logged_in_user():
    token = session.get("token")
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            return User.query.get(payload["user_id"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    return None

# GitHub OAuth blueprint should be created before using it
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    redirect_url="/profile",
    scope="read:user,user:email"
)

# Register the blueprint before using it
app.register_blueprint(github_bp, url_prefix="/login")

# OAuth error handler
@oauth_error.connect_via(github_bp)  # Now this should work
def github_oauth_error(blueprint, message, response):
    flash("GitHub OAuth error: " + message, "danger")
    session.clear()
    return redirect(url_for("home"))


# Routes
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def home():
    if session.get("user_id") or github.authorized:
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

        # Generate JWT token
        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(days=3)  # Token expires in 3 days
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

        session["token"] = token
        log_login(user.id)
        flash("Login successful!", "success")
        return redirect(url_for("profile"))

    return render_template("login.html")

@app.route("/profile")
def profile():
    # GitHub OAuth
    if github.authorized:
        try:
            resp = github.get("/user")
            if not resp.ok:
                session.clear()
                return redirect(url_for("home"))
            user_info = resp.json()
            github_id = str(user_info["id"])
            username = user_info["login"]

            email = user_info.get("email")
            if not email:
                emails_resp = github.get("/user/emails")
                if emails_resp.ok:
                    emails = emails_resp.json()
                    email = next((e["email"] for e in emails if e["primary"] and e["verified"]), None)
                email = email or f"{username}@users.noreply.github.com"

            user = User.query.filter_by(github_id=github_id).first()
            if not user:
                user = User(username=username, email=email, github_id=github_id, auth_method="github")
                db.session.add(user)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    flash("GitHub user already exists with same username or email.", "warning")

            session["user_id"] = user.id
            log_login(user.id)
            return render_template("profile.html", user=user)

        except Exception as e:
            print("GitHub error:", e)
            session.clear()
            return redirect(url_for("home"))

    # Manual login
    user = get_logged_in_user()
    if not user:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
