import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
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
    """Renders the homepage displaying all aquariums."""
    # Get all aquariums from the database
    all_aquariums = aquariums.get_aquariums()

    # Render the "index.html" template, passing the list of aquariums
    return render_template("index.html", aquariums=all_aquariums)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Renders the page for a specific user."""
    # Get the user details using the provided user ID
    user = users.get_user(user_id)
    # Check if the user exists
    if not user:
        # If not, raise a 404 Not Found error
        abort(404)

    # Render the "show_user.html" template with the user details
    return render_template("show_user.html", user=user)

@app.route("/search")
def search():
    """Renders the search page and results based on user query."""
    # Get the search query
    query = request.args.get("query")
    # If a query is provided, search for matching aquariums - otherwise, return an empty list
    results = aquariums.search(query) if query else []

    # Render the "search.html" template with the search query and results
    return render_template("search.html", query=query, results=results)

@app.route("/aquarium/<int:aquarium_id>")
def show_aquarium(aquarium_id):
    """Renders the page for a specific aquarium."""
    # Get the aquarium details using the provided aquarium ID
    aquarium = aquariums.get_aquarium(aquarium_id)
    # Check if the aquarium exists
    if not aquarium:
        # If not, raise a 404 Not Found error
        abort(404)

    # Render the "show_aquarium.html" template with the aquarium details
    return render_template("show_aquarium.html", aquarium=aquarium)

@app.route("/new_aquarium")
def new_aquarium():
    """Renders the page for creating a new aquarium."""
    # Ensure the user is logged in before allowing access to this page
    require_login()

    # Render the "new_aquarium.html" template for the user to fill out
    return render_template("new_aquarium.html")

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    """Creates a new aquarium based on user input."""
    # Ensure the user is logged in before allowing access to this function
    require_login()

    # Get the user ID from the session to associate the aquarium with the user
    user_id = session["user_id"]
    # Get the aquarium details from the submitted form data
    name = request.form["name"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    # Validate that the details were provided correctly
    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000
    # Add the new aquarium into the database using the provided details
    aquariums.add_aquarium(user_id, name, dims, volume, description)

    # Redirect to the homepage after successfully creating the aquarium
    return redirect("/")

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    """Renders the page for editing a specific aquarium."""
    # Ensure the user is logged in before allowing access to this page
    require_login()

    # Get the aquarium details using the provided aquarium ID
    aquarium = aquariums.get_aquarium(aquarium_id)

    # Check if the aquarium exists
    if not aquarium:
        # If not, raise a 404 Not Found error
        abort(404)
    # Check that the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        # If not, raise a 403 Forbidden error
        abort(403)

    # Render the "edit_aquarium.html" template with the aquarium details
    return render_template("edit_aquarium.html", aquarium=aquarium)

@app.route("/update_aquarium", methods=["POST"])
def update_aquarium():
    """Updates the details of an existing aquarium based on user input."""
    # Ensure the user is logged in before allowing access to this function
    require_login()

    # Get the aquarium ID from the hidden field on the form
    aquarium_id = request.form["aquarium_id"]
    # Get the aquarium details using the aquarium ID
    aquarium = aquariums.get_aquarium(aquarium_id)

    # Check if the aquarium exists
    if not aquarium:
        # If not, raise a 404 Not Found error
        abort(404)
    # Check that the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        # If not, raise a 403 Forbidden error
        abort(403)

    # Get the updated details from the form
    name = request.form["name"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    # Validate that the details are provided correctly
    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000
    # Update the aquarium details in the database
    aquariums.update_aquarium(name, dims, volume, description, aquarium_id)

    # Redirect to the updated aquarium's page
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    """Handles the removal of an aquarium."""
    # Ensure the user is logged in before allowing access to this function
    require_login()

    # Get the aquarium details using the aquarium ID
    aquarium = aquariums.get_aquarium(aquarium_id)

    # Check if the aquarium exists
    if not aquarium:
        # If not, raise a 404 Not Found error
        abort(404)
    # Check that the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        # If not, raise a 403 Forbidden error
        abort(403)

     # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_aquarium.html", aquarium=aquarium)

    # Remove or cancel the aquarium
    if request.method == "POST":
        # Check if the user confirmed the removal
        if "remove" in request.form:
            # Remove the aquarium from the database
            aquariums.remove_aquarium(aquarium_id)
            # Redirect to the homepage after successful removal
            return redirect("/")
        # If removal was cancelled, redirect back to the aquarium's page
        return redirect("/aquarium/" + str(aquarium_id))

@app.route("/register")
def register():
    """Renders the registration page."""
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    """Handles the creation of a new user account."""
    # Get the username and passwords from the form
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    # Validate length of username
    if not username or len(username) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")
    # Validate length of passwords
    if not password1 or len(password1) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")
    if not password2 or len(password2) > 50:
        abort(400, description="Name is required and must be 50 characters or less.")

    # Check if the two passwords match
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat" # Error message for passwords that do not match
    # Hash the password for security
    password_hash = generate_password_hash(password1)

    try:
        # Insert the new user into the database
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        # Raise an error if the username is already taken
        return "VIRHE: tunnus on jo varattu" # Error message for username already taken

    # Return a success message if the account is created
    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login functionality."""
    # Display the login form
    if request.method == "GET":
        return render_template("login.html")

    # Process the login
    if request.method == "POST":
        # Retrieve username and password from the form
        username = request.form["username"]
        password = request.form["password"]

        # Get the user's hashed password from the database
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        # Check if the username exists in the database
        if not result:
            return "VIRHE: väärä tunnus" # Error message for incorrect username

        # Extract user ID and password hash from the query result
        result = result[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        # Verify the provided password against the stored hash
        if check_password_hash(password_hash, password):
            # Store user ID and username in the session if login is successful
            session["user_id"] = user_id
            session["username"] = username
            # Redirect to the homepage upon successful login
            return redirect("/")
        # Return error message if the password is incorrect
        return "VIRHE: väärä salasana" # Error message for incorrect password

@app.route("/logout")
def logout():
    """Handles user logout functionality."""
    # Check if the user is logged in
    if "user_id" in session:
        # Remove user ID and username from the session to log out
        del session["user_id"]
        del session["username"]

    # Redirect to the homepage after logging out
    return redirect("/")
