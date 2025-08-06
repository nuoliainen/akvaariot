import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort, flash
import markupsafe
import db
import config
import aquariums
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    """Ensures that the user is logged in."""
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
        l, d, h = int(dims[0]), int(dims[1]), int(dims[2])
        # Check that each dimension is within a correct range
        if not 0 < l < 10000 or not 0 < d < 10000 or not 0 < h < 10000:
            abort(400, description="Dimensions must be positive integers from 1 to 9999 cm.")
    except (ValueError, KeyError):
        abort(400, description="Dimensions must be positive integers from 1 to 9999 cm.")

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    """Renders the homepage displaying all aquariums."""
    all_aquariums = aquariums.get_aquariums()
    return render_template("index.html", aquariums=all_aquariums)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Renders the page for a specific user showing their aquariums."""
    user = users.get_user(user_id)
    # Check if the user exists
    if not user:
        abort(404)

    aquariums = users.get_aquariums(user_id)

    return render_template("show_user.html", user=user, aquariums=aquariums)

@app.route("/search")
def search():
    """Renders the search page and results based on user query."""
    query = request.args.get("query")
    # If a query is provided, search for matching aquariums - otherwise, return an empty list
    results = aquariums.search(query) if query else []

    return render_template("search.html", query=query, results=results)

@app.route("/aquarium/<int:aquarium_id>")
def show_aquarium(aquarium_id):
    """Renders the page for a specific aquarium."""
    aquarium = aquariums.get_aquarium(aquarium_id)
    # Check if the aquarium exists
    if not aquarium:
        abort(404)

    return render_template("show_aquarium.html", aquarium=aquarium)

@app.route("/new_aquarium")
def new_aquarium():
    """Renders the page for creating a new aquarium."""
    require_login()
    return render_template("new_aquarium.html")

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    """Creates a new aquarium based on user input.
    Validates that the input is correct and calculates the volume."""
    require_login()

    user_id = session["user_id"]
    name = request.form["name"]
    date = request.form["date"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000
    aquariums.add_aquarium(user_id, name, dims, volume, date, description)

    return redirect("/")

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    """Renders the page for editing a specific aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    # Check if the aquarium exists
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    return render_template("edit_aquarium.html", aquarium=aquarium)

@app.route("/update_aquarium", methods=["POST"])
def update_aquarium():
    """Updates the details of an existing aquarium based on user input.
    Validates that the input is correct and calculates the volume."""
    require_login()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    # Check if the aquarium exists
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    name = request.form["name"]
    date = request.form["date"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000
    aquariums.update_aquarium(name, dims, volume, date, description, aquarium_id)

    # Redirect to the updated aquarium's page
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    """Handles the removal of an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    # Check if the aquarium exists
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_aquarium.html", aquarium=aquarium)

    # Remove aquarium or cancel action
    if request.method == "POST":
        if "remove" in request.form:
            aquariums.remove_aquarium(aquarium_id)
            return redirect("/")
        # If removal was cancelled, redirect back to the aquarium's page
        return redirect("/aquarium/" + str(aquarium_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles the creation of a new user account."""
    if request.method == "GET":
        return render_template("register.html", filled={})

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        # Validate length of username
        if not username or len(username) > 50:
            abort(400, description="Name is required and must be 50 characters or less.")
        # Validate length of passwords
        if not password1 or len(password1) > 50:
            abort(400, description="Password is required and must be 50 characters or less.")
        if not password2 or len(password2) > 50:
            abort(400, description="Password is required and must be 50 characters or less.")

        if password1 != password2:
            flash("VIRHE: salasanat eivät ole samat")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        try:
            users.create_user(username, password1)
        except sqlite3.IntegrityError:
            flash("VIRHE: tunnus on jo varattu")
            filled = {"username": username}
            return render_template("register.html", filled=filled)

        flash("Tunnuksen luonti onnistui!")
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login functionality."""
    # Display the login form
    if request.method == "GET":
        return render_template("login.html")

    # Process the login
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            flash("VIRHE: Väärä tunnus tai salasana!")
            return redirect("/login")

@app.route("/logout")
def logout():
    """Handles user logout functionality."""
    if "user_id" in session:
        del session["user_id"]
        del session["username"]

    return redirect("/")
