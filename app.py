import sqlite3
import db
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import aquariums

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_aquarium")
def new_aquarium():
    return render_template("new_aquarium.html")

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    user_id = session["user_id"]
    name = request.form["name"]
    l = int(request.form["length"])
    d = int(request.form["depth"])
    h = int(request.form["height"])
    description = request.form["description"]
    volume = l*d*h//1000 # calculate volume in liters

    aquariums.add_aquarium(user_id, name, l, d, h, volume, description)

    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        if not result:
            return "VIRHE: väärä tunnus"
        else:
            result = result[0]
            user_id = result["id"]
            password_hash = result["password_hash"]

            if check_password_hash(password_hash, password):
                session["user_id"] = user_id
                session["username"] = username
                return redirect("/")
            else:
                return "VIRHE: väärä salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")