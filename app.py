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
    all_aquariums = aquariums.get_aquariums()
    return render_template("index.html", aquariums=all_aquariums)

@app.route("/aquarium/<int:aquarium_id>")
def page(aquarium_id):
    aquarium = aquariums.get_aquarium(aquarium_id)
    return render_template("show_aquarium.html", aquarium=aquarium)

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
    volume = l*d*h//1000 # Calculate volume in liters

    # Check that the name is at least 1 character long
    if len(name) < 1:
        return "VIRHE: Akvaarion nimen tulee olla vähintään yhden merkin pituinen!"

    aquariums.add_aquarium(user_id, name, l, d, h, volume, description)
    return redirect("/")

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    aquarium = aquariums.get_aquarium(aquarium_id)
    return render_template("edit_aquarium.html", aquarium=aquarium)

@app.route("/update_aquarium", methods=["POST"])
def update_aquarium():
    aquarium_id = request.form["aquarium_id"]
    name = request.form["name"]
    l = int(request.form["length"])
    d = int(request.form["depth"])
    h = int(request.form["height"])
    description = request.form["description"]
    volume = l*d*h//1000 # Calculate volume in liters

    # Check that the name is at least 1 character long
    if len(name) < 1:
        return "VIRHE: Akvaarion nimen tulee olla vähintään yhden merkin pituinen!"

    aquariums.update_aquarium(name, l, d, h, volume, description, aquarium_id)
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    if request.method == "GET":
        aquarium = aquariums.get_aquarium(aquarium_id)
        return render_template("remove_aquarium.html", aquarium=aquarium)

    if request.method == "POST":
        if "remove" in request.form:
            aquariums.remove_aquarium(aquarium_id)
            return redirect("/")
        else:
            return redirect("/aquarium/" + str(aquarium_id))

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