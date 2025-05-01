
# 🔐 Flask GitHub OAuth 2.0 Authentication

This project demonstrates how to implement GitHub OAuth 2.0 login in a Flask web application using the Flask-Dance library. It allows users to authenticate via GitHub or manually using a username and password. The app features secure password storage, session management, and login activity logging.

---

## 📘 Project Overview

This Flask application provides the following features:

- **Manual Authentication**: Users can sign up and log in using their email/username and password.
- **GitHub OAuth Authentication**: Users can log in using their GitHub account.
- **Secure Password Management**: Passwords are hashed with bcrypt before storing them in the database.
- **Session Management**: The app manages sessions for logged-in users and prevents session backtracking.
- **Login Logging**: Every login attempt is logged along with the user's IP address and timestamp.

The app uses the Flask framework, Flask-Dance for OAuth, and SQLAlchemy for database interactions. After logging in, users are redirected to a profile page displaying their GitHub information (username, email, avatar).

---

## 🛠 How to Run the Project

### Step 1: Set the Execution Policy (for Windows PowerShell)

If you’re on Windows, you’ll need to allow script execution in PowerShell:

```bash
Set-ExecutionPolicy RemoteSigned -Scope Process
```

This step ensures that PowerShell can run local scripts, including those needed to activate the virtual environment.

---

### Step 2: Activate the Virtual Environment

Activate the virtual environment to install and manage dependencies:

```bash
.\venv\Scripts\Activate.ps1
```

This command activates the virtual environment where all the project dependencies will be installed.

---

### Step 3: Install Project Dependencies

Install the required dependencies listed in `requirements.txt`:

```bash
pip install -r .\requirements.txt
```

This will install all necessary Python packages for the project, including Flask, Flask-Dance, SQLAlchemy, and bcrypt.

---

### Step 4: Run the Flask Application

Start the Flask development server:

```bash
flask run --host=localhost
```

This will launch the app on `http://localhost:5000`. You can visit this URL in your browser to interact with the application.

---

### 🎉 You’re all set! The app should now be running locally.


