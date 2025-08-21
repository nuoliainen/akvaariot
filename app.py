import sqlite3
import secrets
from flask import Flask
from flask import redirect, render_template, request, session, abort, flash, make_response, g
import markupsafe
import math
import time
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

def require_owner(item):
    """Ensures that the current user is the owner of the item and that the item exists."""
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
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

def get_aquarium_data():
    """Gets and validates aquarium name, date, description and dimensions from the form."""
    name = request.form["name"]
    date = request.form["date"]
    description = request.form["description"]
    dims = [request.form["length"], request.form["depth"], request.form["height"]]

    validate_input(name, description, dims)
    # Calculate volume in liters using the provided dimensions (cm)
    volume = int(dims[0])*int(dims[1])*int(dims[2]) // 1000

    return name, date, description, dims, volume

def get_validated_classes():
    all_classes = aquariums.get_all_classes()
    classes = []

    # Get and validate all submitted class entries (title, value) from the form
    for entry in request.form.getlist("classes"):
        if entry:
            title, value = entry.split(":")
            if title not in all_classes or value not in all_classes[title]:
                abort(403)
            classes.append((title, value))

    return classes

def get_critter_data():
    """Gets and validates critter species name and inumber of individuals."""
    species = request.form["species"]
    count = request.form["count"]

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

    return species, count

@app.template_filter()
def show_lines(content):
    """Template filter to safely display line breaks."""
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    """Renders the homepage displaying all aquariums."""
    page_size = 10
    aquarium_count = aquariums.count_aquariums()
    page_count = math.ceil(aquarium_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_aquariums = aquariums.get_aquariums_page(page, page_size)
    return render_template("index.html",
                           aquariums=all_aquariums,
                           page=page,
                           page_count=page_count,
                           current_page="index")

@app.route("/user/<int:user_id>")
def show_user(user_id):
    """Renders the page for a specific user showing their aquariums."""
    user = users.get_user(user_id)
    # Check if the user exists
    if not user:
        abort(404)

    user_aquariums = users.get_aquariums(user_id)
    critter_counts = users.count_critters(user_id)
    return render_template("show_user.html", user=user, aquariums=user_aquariums,
                           critter_counts=critter_counts, current_page="userpage")

@app.route("/aquarium/<int:aquarium_id>")
def show_aquarium(aquarium_id):
    """Renders the page for a specific aquarium."""
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)

    max_comments = 10
    classes = aquariums.get_selected_classes(aquarium_id)
    critters = aquariums.get_critters(aquarium_id)
    newest_comments = aquariums.get_newest_comments(aquarium_id, max_comments)
    total_comments = aquariums.count_comments(aquarium_id)
    images = aquariums.get_images(aquarium_id)
    main_image = aquariums.get_main_image(aquarium_id)

    return render_template("show_aquarium.html",
                           aquarium=aquarium, classes=classes, critters=critters,
                           comments=newest_comments, total_comments=total_comments,
                           max_comments=max_comments, images=images, main_image=main_image)

@app.route("/new_aquarium")
def new_aquarium():
    """Renders the page for creating a new aquarium."""
    require_login()
    classes = aquariums.get_all_classes()
    return render_template("new_aquarium.html", classes=classes, current_page="new_aquarium")

@app.route("/create_aquarium", methods=["POST"])
def create_aquarium():
    """Creates a new aquarium based on user input.
    Validates that the input is correct and calculates the volume."""
    require_login()
    check_csrf()

    user_id = session["user_id"]
    name, date, description, dims, volume = get_aquarium_data()
    aquariums.add_aquarium(user_id, name, dims, volume, date, description)
    aquarium_id = db.last_insert_id()

    classes = get_validated_classes()
    aquariums.add_aquarium_classes(aquarium_id, classes)
    flash("Akvaario luotu!", "success")
    flash("Voit nyt lisätä akvaarioon eläimiä ja kuvia.", "info")

    # Redirect to the page of the new aquarium
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/edit_aquarium/<int:aquarium_id>")
def edit_aquarium(aquarium_id):
    """Renders the page for editing a specific aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    # Get all classes to display the available options in the form
    all_classes = aquariums.get_all_classes()
    # Get the classes of the specific aquarium to display as default values
    classes = {class_title: "" for class_title in all_classes}
    for entry in aquariums.get_selected_classes(aquarium_id):
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
    require_owner(aquarium)

    name, date, description, dims, volume = get_aquarium_data()
    classes = get_validated_classes()

    aquariums.update_aquarium(name, dims, volume, date, description, aquarium_id, classes)
    flash("Akvaarion muokkaus onnistui!", "success")

    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_aquarium/<int:aquarium_id>", methods=["GET", "POST"])
def remove_aquarium(aquarium_id):
    """Handles the removal of an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_aquarium.html", aquarium=aquarium)

    # Remove aquarium
    if request.method == "POST":
        check_csrf()
        aquariums.remove_aquarium(aquarium_id)
        flash("Poistettu!", "success")
        return redirect("/user/" + str(session["user_id"]))

@app.route("/new_critter")
def new_critter():
    """Renders the page for creating a new critter."""
    require_login()
    # Get all aquariums of the user to display options for changing the target aquarium
    user_aquariums = users.get_aquariums(session["user_id"])

    if not user_aquariums:
        flash("Sinun pitää luoda ainakin yksi akvaario ennen eläinten lisäämistä.", "warning")
        return redirect("/new_aquarium")

    # Get the default selected aquarium from query parameters (if present)
    selected_aquarium_id = request.args.get("aquarium_id", type=int)

    return render_template("new_critter.html",
                           aquariums=user_aquariums,
                           selected_aquarium_id=selected_aquarium_id,
                           current_page="new_critter")

@app.route("/create_critter", methods=["POST"])
def create_critter():
    """Creates a new critter based on user input.
    Validates that the input is correct."""
    require_login()
    check_csrf()

    user_id = session["user_id"]
    user_aquariums = users.get_aquariums(user_id)
    if not user_aquariums:
        flash("Sinun pitää luoda ainakin yksi akvaario ennen eläinten lisäämistä.", "warning")
        return redirect("/new_aquarium")

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    species, count = get_critter_data()
    aquariums.add_critter(user_id, aquarium_id, species, count)
    flash("Eläin lisätty!", "success")
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/edit_critter/<int:critter_id>")
def edit_critter(critter_id):
    """Renders the page for editing a specific critter."""
    require_login()

    critter = aquariums.get_critter(critter_id)
    require_owner(critter)

    # Get all aquariums of the user to display options for changing the target aquarium
    user_aquariums = users.get_aquariums(session["user_id"])
    return render_template("edit_critter.html", critter=critter, aquariums=user_aquariums)

@app.route("/update_critter", methods=["POST"])
def update_critter():
    """Updates the details of an existing critter based on user input."""
    require_login()
    check_csrf()

    critter_id = request.form["critter_id"]
    critter = aquariums.get_critter(critter_id)
    require_owner(critter)

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    species, count = get_critter_data()
    aquariums.update_critter(species, count, aquarium_id, critter_id)
    flash("Eläimen muokkaus onnistui!", "success")
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_critter/<int:critter_id>", methods=["GET", "POST"])
def remove_critter(critter_id):
    """Handles the removal of a critter."""
    require_login()

    critter = aquariums.get_critter(critter_id)
    require_owner(critter)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_critter.html", critter=critter)

    # Remove critter or cancel action
    if request.method == "POST":
        check_csrf()
        aquariums.remove_critter(critter_id)
        flash(f"{critter["species"]} ({critter["count"]} kpl) poistettu akvaariosta!", "success")
        return redirect("/aquarium/" + str(critter["aquarium_id"]))

@app.route("/remove_critters/<int:aquarium_id>", methods=["GET", "POST"])
def remove_critters(aquarium_id):
    """Handles the removal of all critters in an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    critters = aquariums.get_critters(aquarium_id)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_critters.html", aquarium=aquarium, critters=critters)

    # Remove critter or cancel action
    if request.method == "POST":
        check_csrf()
        aquariums.remove_critters(aquarium_id)
        flash(f"Kaikki eläimet poistettu akvaariosta!", "success")
        return redirect("/aquarium/" + str(aquarium_id))

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

    # If comment was sent from page showing all comments, return to that page
    if "show_comments" in request.form:
        return redirect("/aquarium/" + str(aquarium_id) + "/comments")
    # Otherwise return to aquarium page
    return redirect("/aquarium/" + str(aquarium_id))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    """Handles the removal of a comment."""
    require_login()

    comment = aquariums.get_comment(comment_id)
    require_owner(comment)

    # Show the removal confirmation/cancellation page
    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)

    # Remove comment
    if request.method == "POST":
        check_csrf()
        aquariums.remove_comment(comment_id)
        flash("Poistettu!", "success")
        # Redirect back depending on which page the removal was initiated
        next_url = request.args.get("next")
        return redirect(next_url or ("/aquarium/" + str(comment["aquarium_id"])))

@app.route("/aquarium/<int:aquarium_id>/comments")
@app.route("/aquarium/<int:aquarium_id>/comments/<int:page>")
def show_comments(aquarium_id, page=1):
    """Renders the page for showing all comments of a specific aquarium."""
    aquarium = aquariums.get_aquarium(aquarium_id)
    if not aquarium:
        abort(404)

    page_size = 20
    comment_count = aquariums.count_comments(aquarium_id)
    page_count = math.ceil(comment_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect(f"/aquarium/{aquarium_id}/comments/1")
    if page > page_count:
        return redirect(f"/aquarium/{aquarium_id}/comments/{page_count}")

    comments = aquariums.get_comments_page(aquarium_id, page, page_size)
    total_comments = aquariums.count_comments(aquarium_id)

    return render_template("show_comments.html",
                           aquarium=aquarium, comments=comments, total_comments=total_comments,
                           page=page, page_count=page_count)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image, file_type = aquariums.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", file_type)
    return response

@app.route("/images/<int:aquarium_id>")
def manage_images(aquarium_id):
    """Renders the page for adding and removing images of an aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    images = aquariums.get_images(aquarium_id)
    image_count = aquariums.count_images(aquarium_id)
    main_image = aquariums.get_main_image(aquarium_id)
    return render_template("images.html", aquarium=aquarium, images=images,
                           image_count=image_count, main_image=main_image)

@app.route("/add_image", methods=["POST"])
def add_image():
    """Adds an image to the aquarium."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    max_images = 6
    max_file_size = 100 * 1024
    allowed_file_types = [".png", ".jpg", ".jpeg"]

    count = aquariums.count_images(aquarium_id)
    if count >= max_images:
        flash("Olet lisännyt akvaariolle jo maksimimäärän kuvia.", "warning")
        return redirect("/images/" + str(aquarium_id))

    file = request.files["image"]
    if not any(file.filename.lower().endswith(file_type) for file_type in allowed_file_types):
        flash("Väärä tiedostomuoto! Sallitut tiedostot: .png, .jpg ja .jpeg", "error")
        return redirect("/images/" + str(aquarium_id))

    image = file.read()
    file_type = file.content_type # image/png or image/jpg etc.
    print(file_type)
    if len(image) > max_file_size:
        flash("Liian suuri kuva!", "error")
        return redirect("/images/" + str(aquarium_id))

    aquariums.add_image(aquarium_id, image, file_type)
    image_id = db.last_insert_id()
    # Set the first image uploaded as the main image
    if count == 0:
        aquariums.set_main_image(aquarium_id, image_id)
    flash("Kuva lisätty!", "success")
    return redirect("/images/" + str(aquarium_id))

@app.route("/set_main_image", methods=["POST"])
def set_main_image():
    """Sets the chosen image as the main image."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    image_id = request.form["image_id"]

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    aquariums.set_main_image(aquarium_id, image_id)

    flash("Pääkuva vaihdettu!", "success")
    return redirect("/images/" + str(aquarium_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    """Removes one or multiple images from the aquarium."""
    require_login()
    check_csrf()

    aquarium_id = request.form["aquarium_id"]
    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    image_ids = request.form.getlist("image_id")
    if image_ids:
        current_main_image_id = aquariums.get_main_image(aquarium_id)
        aquariums.remove_images(image_ids, aquarium_id)

        # If main image was removed, set a new one
        if str(current_main_image_id) in image_ids:
            # Find the oldest remaining image
            oldest_image_id = aquariums.get_oldest_image(aquarium_id)
            if oldest_image_id:
                aquariums.set_main_image(aquarium_id, oldest_image_id)

        flash("Kuva(t) poistettu!", "success")
    return redirect("/images/" + str(aquarium_id))

@app.route("/remove_all_images/<int:aquarium_id>", methods=["GET", "POST"])
def remove_all_images(aquarium_id):
    """Removes all images from the aquarium."""
    require_login()

    aquarium = aquariums.get_aquarium(aquarium_id)
    require_owner(aquarium)

    if request.method == "GET":
        return render_template("remove_all_images.html", aquarium=aquarium)

    if request.method == "POST":
        check_csrf()
        images = aquariums.get_images(aquarium_id)
        if images:
            aquariums.remove_all_images(aquarium_id)
            flash("Kaikki akvaarion kuvat poistettu!", "success")
        return redirect("/images/" + str(aquarium_id))

@app.route("/search")
@app.route("/search/<int:page>")
def search(page=1):
    """Renders the search page and results based on user search conditions."""
    all_classes = aquariums.get_all_classes()

    filters = {
        "query": request.args.get("query"),
        "species_query": request.args.get("species_query"),
        "volume_min": request.args.get("volume_min", "", type=int),
        "volume_max": request.args.get("volume_max", "", type=int),
        "date_min": request.args.get("date_min"),
        "date_max": request.args.get("date_max")
    }

    for class_title in aquariums.get_all_classes().keys():
        value = request.args.get(f"class_{class_title}")
        filters[f"class_{class_title}"] = value

    if not any(filters.values()):
        return render_template("search.html",
                               all_classes=all_classes,
                               results=[],
                               filters=filters,
                               page=1,
                               page_count=1,
                               current_page="search")

    page_size = 10
    result_count = aquariums.count_search_results(filters)
    page_count = math.ceil(result_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        query_string = request.query_string.decode()
        return redirect(f"/search/1?{query_string}")
    if page > page_count:
        query_string = request.query_string.decode()
        return redirect(f"/search/{page_count}?{query_string}")

    results = aquariums.search_page(filters, page, page_size)
    return render_template("search.html",
                           all_classes=all_classes,
                           results=results,
                           result_count=result_count,
                           filters=filters,
                           page=page,
                           page_count=page_count,
                           current_page="search")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles the creation of a new user account."""
    if request.method == "GET":
        return render_template("register.html", filled={}, current_page="register")

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
            flash("Salasanat eivät ole samat!", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, current_page="register")

        try:
            users.create_user(username, password1)
        except sqlite3.IntegrityError:
            flash("Tunnus on jo varattu!", "error")
            filled = {"username": username}
            return render_template("register.html", filled=filled, current_page="register")

        flash("Tunnuksen luonti onnistui! Voit nyt kirjautua sisään.", "success")
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login functionality."""
    # Display the login form
    if request.method == "GET":
        return render_template("login.html", current_page="login")

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
        flash("Väärä tunnus tai salasana!", "error")
        return redirect("/login")

@app.route("/logout")
def logout():
    """Handles user logout functionality."""
    if "user_id" in session:
        del session["user_id"]
        del session["username"]

    return redirect("/")
