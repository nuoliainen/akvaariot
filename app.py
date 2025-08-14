import sqlite3
import secrets
from flask import Flask
from flask import redirect, render_template, request, session, abort, flash, make_response
import markupsafe
import math
import config
import aquariums
import users
import db

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    """Ensures that the user is logged in."""
    if "user_id" not in session:
        abort(403)

def check_csrf():
    """Validates the CSRF token."""
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
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
    """Template filter to safely display line breaks."""
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    """Renders the homepage displaying all aquariums."""
    page_size = 10
    aquarium_count = aquariums.aquarium_count()
    page_count = math.ceil(aquarium_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_aquariums = aquariums.get_aquariums_page(page, page_size)
    return render_template("index.html", aquariums=all_aquariums, page=page, page_count=page_count)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Renders the page for a specific user showing their aquariums."""
    user = users.get_user(user_id)
    # Check if the user exists
    if not user:
        abort(404)

    user_aquariums = users.get_aquariums(user_id)
    return render_template("show_user.html", user=user, aquariums=user_aquariums)

@app.route("/search")
def search():
    """Renders the search page and results based on user query."""
    query = request.args.get("query")
    results = aquariums.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/images/<int:aquarium_id>")
def edit_images(aquarium_id):
    """Renders the page for editing images of an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    images = aquariums.get_images(aquarium_id)
    return render_template("images.html", aquarium=aquarium, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    """Adds an image to the aquarium."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith((".png")):
        flash("VIRHE: väärä tiedostomuoto")
        return redirect("/images/" + str(aquarium_id))

    image = file.read()
    if len(image) > 100 * 1024:
        flash("VIRHE: liian suuri kuva")
        return redirect("/images/" + str(aquarium_id))

    aquariums.add_image(aquarium_id, image)
    flash("Kuva lisätty!")
    return redirect("/images/" + str(aquarium_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    """Removes one or multiple images from the aquarium."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        aquariums.remove_image(image_id, aquarium_id)

    flash("Kuva(t) poistettu!")
    return redirect("/images/" + str(aquarium_id))

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = aquariums.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/aquarium/<int:aquarium_id>")
def show_aquarium(aquarium_id):
    """Renders the page for a specific aquarium."""
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)

    classes = aquariums.get_aquarium_classes(aquarium_id)
    critters = aquariums.get_critters(aquarium_id)
    comments = aquariums.get_comments(aquarium_id)
    images = aquariums.get_images(aquarium_id)

    return render_template("show_aquarium.html",
                           aquarium=aquarium, classes=classes, critters=critters, comments=comments,
                           images=images)

@app.route("/new_aquarium")
def new_aquarium():
    """Renders the page for creating a new aquarium."""
    require_login()
    classes = aquariums.get_all_classes()
    return render_template("new_aquarium.html", classes=classes)

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    """Creates a new aquarium based on user input.
    Validates that the input is correct and calculates the volume."""
    require_login()
    check_csrf()

    user_id = session["user_id"]
    name = request.form["name"]
    date = request.form["date"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000

    all_classes = aquariums.get_all_classes()
    classes = []
    # Get and validate all submitted class entries (title, value) from the form
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes:
                abort(403)
            if value not in all_classes[title]:
                abort(403)
            classes.append((title, value))

    aquariums.add_aquarium(user_id, name, dims, volume, date, description, classes)
    # Redirect to the page of the new aquarium
    return redirect("/aquarium/" + str(db.last_insert_id()))

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    """Renders the page for editing a specific aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    # Get all classes to display the available options in the form
    all_classes = aquariums.get_all_classes()
    # Get the classes of the specific aquarium to display as default values
    classes = {class_title: "" for class_title in all_classes}
    for entry in aquariums.get_aquarium_classes(aquarium_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_aquarium.html",
                           aquarium=aquarium, all_classes=all_classes, classes=classes)

@app.route("/update_aquarium", methods=["POST"])
def update_aquarium():
    """Updates the details of an existing aquarium based on user input.
    Validates that the input is correct and calculates the volume."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    if "save" in request.form:
        name = request.form["name"]
        date = request.form["date"]
        description = request.form["description"]
        dims = [request.form["length"], request.form["depth"], request.form["height"]]

        validate_input(name, description, dims)
        # Calculate volume in liters using the provided dimensions (cm)
        volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000

        all_classes = aquariums.get_all_classes()
        classes = []
        # Get and validate all submitted class entries (title, value) from the form
        for entry in request.form.getlist("classes"):
            if entry:
                title, value = entry.split(":")
                if title not in all_classes:
                    abort(403)
                if value not in all_classes[title]:
                    abort(403)
                classes.append((title, value))

        aquariums.update_aquarium(name, dims, volume, date, description, aquarium_id, classes)

    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    """Handles the removal of an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
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
        check_csrf()
        if "remove" in request.form:
            aquariums.remove_aquarium(aquarium_id)
            return redirect("/")
        # If removal was cancelled, redirect back to the aquarium's page
        return redirect("/aquarium/" + str(aquarium_id))

@app.route("/new_critter")
def new_critter():
    """Renders the page for creating a new critter."""
    require_login()
    # Get all aquariums of the user to display options for changing the target aquarium
    user_aquariums = users.get_aquariums(session["user_id"])
    return render_template("new_critter.html", aquariums=user_aquariums)

@app.route("/create_critter", methods=["POST"])
def create_critter():
    """Creates a new critter based on user input.
    Validates that the input is correct."""
    require_login()
    check_csrf()

    user_id = session["user_id"]
    aquarium_id = request.form["aquarium_id"]
    species = request.form["species"]
    count = request.form["count"]

    # Check if the aquarium exists
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)
    # Ensure the logged-in user is the owner of the aquarium
    if aquarium["user_id"] != session["user_id"]:
        abort(403)

    # Validate length of species name
    if len(species) < 1 or len(species) > 100:
        abort(400, description="Species name is required and must be 100 characters or less.")

    # Validate count of individuals
    try:
        count = int(count)
        if count < 1 or count > 9999:
            abort(400, description="Group size must be between 1 and 9999.")
    except (ValueError, KeyError):
        abort(400, description="Group size must be a positive integer from 1 to 9999.")

    aquariums.add_critter(user_id, aquarium_id, species, count)
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_critter/<int:critter_id>", methods=["GET", "POST"])
def remove_critter(critter_id):
    """Handles the removal of a critter."""
    require_login()

    critter = aquariums.get_critter(critter_id)
    if not critter:
        abort(404)
    # Ensure the logged-in user is the owner of the critter
    if critter["user_id"] != session["user_id"]:
        abort(403)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_critter.html", critter=critter)

    # Remove critter or cancel action
    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            aquariums.remove_critter(critter_id)
        return redirect("/aquarium/" + str(critter["aquarium_id"]))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    """Creates a new comment based on user input.
    Validates that the input is correct."""
    require_login()
    check_csrf()

    user_id = session["user_id"]
    aquarium_id = request.form["aquarium_id"]
    content = request.form["content"]

    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(403)

    if len(content) > 5000:
        abort(400, comment="Comment must be 5000 characters or less.")

    aquariums.add_comment(aquarium_id, user_id, content)

    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    """Handles the removal of a comment."""
    require_login()

    comment = aquariums.get_comment(comment_id)
    if not comment:
        abort(404)
    # Ensure the logged-in user is the author of the comment
    if comment["user_id"] != session["user_id"]:
        abort(403)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)

    # Remove comment or cancel action
    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            aquariums.remove_comment(comment_id)
            flash("Poistettu!")
        return redirect("/aquarium/" + str(comment["aquarium_id"]))

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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        flash("VIRHE: Väärä tunnus tai salasana!")
        return redirect("/login")

@app.route("/logout")
def logout():
    """Handles user logout functionality."""
    if "user_id" in session:
        del session["user_id"]
        del session["username"]

    return redirect("/")
