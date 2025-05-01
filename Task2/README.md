# 🔐 Flask GitHub OAuth 2.0 Authentication

This project demonstrates how to implement GitHub OAuth 2.0 login in a Flask web application using the Flask-Dance library.

---

## 📘 Table of Contents

1. [What is OAuth 2.0?](#what-is-oauth-20)
2. [Project Overview](#project-overview)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Guide](#step-by-step-guide)
    - [1. Create GitHub OAuth App](#1-create-github-oauth-app)
    - [2. Set Environment Variables](#2-set-environment-variables)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Run the Application](#5-run-the-application)
5. [Folder Structure](#folder-structure)

---

## 🤔 What is OAuth 2.0?

OAuth 2.0 is a secure authorization framework that allows third-party applications to access user resources without exposing their credentials (like passwords).

In this project:
- The user logs in using their **GitHub account**.
- The app gets authorized to access **basic profile information** like username and avatar.
- The app does **not** access any sensitive data or password.

---

## 🚀 Project Overview

We use:
- [Flask](https://flask.palletsprojects.com/)
- [Flask-Dance](https://flask-dance.readthedocs.io/) for handling OAuth 2.0
- GitHub as the OAuth Provider

After login, the app displays:
- GitHub username
- Profile image
- Link to GitHub profile

---

## 🧰 Prerequisites

- Python 3.7+
- GitHub account

---

## 🛠 Step-by-Step Guide

### ✅ 1. Create GitHub OAuth App

1. Go to: https://github.com/settings/developers
2. Click **"OAuth Apps"** → **"New OAuth App"**
3. Fill in:
    - **Application Name**: `Flask GitHub OAuth Demo`
    - **Homepage URL**: `http://localhost:5000`
    - **Authorization Callback URL**: `http://localhost:5000/login/github/authorized`
4. Save, and copy:
    - `Client ID`
    - `Client Secret`


---

### ✅ 2. Set Environment Variables

Create a `.env` file in the root of the project:

```
FLASK_SECRET_KEY=your_secret_key
GITHUB_OAUTH_CLIENT_ID=your_client_id
GITHUB_OAUTH_CLIENT_SECRET=your_client_secret
```

---

### ✅ 3. Install Dependencies

Use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

If you don’t have `requirements.txt`, install manually:

```bash
pip install Flask Flask-Dance python-dotenv
```

---

### ✅ 4. Run the Application

```bash
flask run
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🗂 Folder Structure

```
flask-github-oauth/
│
├── app.py                 # Main Flask application
├── .env                  # Environment variables (not tracked by Git)
├── templates/
│   ├── home.html         # Home page template with login button
│   └── profile.html      # User profile page after login
├── venv/                 # Virtual environment (optional)
└── README.md             # Project documentation
```
Here’s the content you can use for your `README.md` file:


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

---

## 🗂 Folder Structure

```
flask-github-oauth/
│
├── app.py                 # Main Flask application
├── .env                  # Environment variables (not tracked by Git)
├── templates/
│   ├── home.html         # Home page template with login button
│   └── profile.html      # User profile page after login
├── venv/                 # Virtual environment (optional)
└── README.md             # Project documentation
```

---

## 🤝 Contributing

If you have any suggestions or improvements for this project, feel free to fork it and submit a pull request.

---

## 💬 License

This project is open-source and available under the MIT License. See the [LICENSE](LICENSE) file for more information.
```

This `README.md` file includes an overview of the project, steps to run it, folder structure, and additional sections for contributing and licensing. You can further customize it as needed.
