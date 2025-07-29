import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import aquariums

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def validate_input(name, description, dims):
    """Validates the input from a form to an aquarium."""
    # Validate length of aquarium name
    if not name or len(name) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")

    # Validate length of description
    if len(description) > 5000:
        abort(400, description="Description must be 5000 characters or less.")

    # Validate dimensions:
    try:
        # Convert dimensions to integers
        l, d, h = int(dims[0]), int(dims[1]), int(dims[2])
        # Check that each dimension is within a correct range
        if not 0 < l < 10000 or not 0 < d < 10000 or not 0 < h < 10000:
            abort(400, description="Dimensions must be positive integers from 1 to 9999 cm.")
    except (ValueError, KeyError):
        # Abort if conversion to integer failed or if dimensions are missing
        abort(400, description="Dimensions must be positive integers from 1 to 9999 cm.")

@app.route("/")
def index():
    all_aquariums = aquariums.get_aquariums()
    return render_template("index.html", aquariums=all_aquariums)

@app.route("/search")
def search():
    query = request.args.get("query")
    results = aquariums.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/aquarium/<int:aquarium_id>")
def page(aquarium_id):
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    return render_template("show_aquarium.html", aquarium=aquarium)

@app.route("/new_aquarium")
def new_aquarium():
    require_login()
    return render_template("new_aquarium.html")

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    require_login()
    user_id = session["user_id"]
    name = request.form["name"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    volume = dims[0]*dims[1]*dims[2] // 1000
    aquariums.add_aquarium(user_id, name, dims, volume, description)
    return redirect("/")

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    require_login()
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    if aquarium["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_aquarium.html", aquarium=aquarium)

@app.route("/update_aquarium", methods=["POST"])
def update_aquarium():
    require_login()
    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    name = request.form["name"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    volume = dims[0]*dims[1]*dims[2] // 1000

    aquariums.update_aquarium(name, dims, volume, description, aquarium_id)

    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    require_login()
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_aquarium.html", aquarium=aquarium)

    if request.method == "POST":
        if "remove" in request.form:
            aquariums.remove_aquarium(aquarium_id)
            return redirect("/")
        return redirect("/aquarium/" + str(aquarium_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or len(username) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")
    if not password1 or len(password1) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")
    if not password2 or len(password2) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")

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

        result = result[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        return "VIRHE: väärä salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")