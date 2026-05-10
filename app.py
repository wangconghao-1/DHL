from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dhl_secret_key'

DB_FILE = 'database.json'

# =========================
# Login Manager Config
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# =========================
# Database Functions
# =========================
def read_db():
    """
    Read database.json
    If file doesn't exist, create default structure
    """

    if not os.path.exists(DB_FILE):
        default_data = {
            "users": [
                {
                    "id": 1,
                    "username": "admin",
                    "password": "123123"
                }
            ],
            "articles": []
        }

        with open(DB_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)

        return default_data

    with open(DB_FILE, 'r') as f:
        return json.load(f)


def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# =========================
# Routes
# =========================

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('index.html')


# =========================
# Login
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        db = read_db()

        users = db.get("users", [])

        user_found = next(
            (
                u for u in users
                if u["username"] == username and u["password"] == password
            ),
            None
        )

        if user_found:
            user = User(id=str(user_found["id"]))
            login_user(user)

            return redirect(url_for('index'))

        return "Invalid credentials", 401

    return render_template('login.html')


# =========================
# Logout
# =========================

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# =========================
# GET Articles
# =========================

@app.route('/api/articles', methods=['GET'])
@login_required
def get_articles():

    db = read_db()

    return jsonify(db.get("articles", []))


# =========================
# CREATE Article
# =========================

@app.route('/api/articles', methods=['POST'])
def create_article():

    try:

        db = read_db()

        articles = db.get("articles", [])

        new_article = request.json

        if not new_article:
            return jsonify({
                "error": "No JSON data received"
            }), 400

        new_article['id'] = len(articles) + 1
        new_article['status'] = 'Draft'

        articles.append(new_article)

        db["articles"] = articles

        write_db(db)

        return jsonify({
            "message": "Article created successfully",
            "article": new_article
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# Run App
# =========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )