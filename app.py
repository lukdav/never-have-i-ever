import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_games")
def get_games():
    categories = list(mongo.db.categories.find())
    games = list(mongo.db.games.find())
    return render_template("games.html", games=games, categories=categories)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    games = list(mongo.db.games.find({"$text": {"$search": query}}))
    return render_template("games.html", games=games)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username Already Exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check hashed password matches input
            if check_password_hash(
              existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Hello {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Incorrect password
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))

        else:
            # Incorrect username
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # get session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    # remover user from session cookies
    flash("You have been logged out.")
    session.pop("user")
    return redirect(url_for('login'))


@app.route("/add_game", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        game = {
            "game_name": request.form.get("game_name"),
            "game_description": request.form.get("game_description"),
            "game_requirements": request.form.getlist("game_requirements"),
            "game_rules": request.form.getlist("game_rules"),
            "category_name": request.form.getlist("category_name"),
            "submitted_by": session["user"],
            "game_rating": 0
            }
        print(game)

        mongo.db.games.insert_one(game)
        flash("Game Submitted")
        return redirect(url_for('get_games'))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_game.html", categories=categories)


@app.route("/edit_game/<game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    if request.method == "POST":
        edit = {
            "game_name": request.form.get("game_name"),
            "game_description": request.form.get("game_description"),
            "game_requirements": request.form.getlist("game_requirements"),
            "game_rules": request.form.getlist("game_rules"),
            "category_name": request.form.getlist("category_name"),
            "submitted_by": session["user"]
            }
        mongo.db.games.update({"_id": ObjectId(game_id)}, edit)
        flash("Game Updated")

    game = mongo.db.games.find_one({"_id": ObjectId(game_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_game.html", game=game, categories=categories)


@app.route("/delete_game/<game_id>")
def delete_game(game_id):
    mongo.db.games.remove({"_id": ObjectId(game_id)})
    flash("Game Deleted")
    return redirect(url_for('get_games'))


@app.route("/game_page/<game_id>")
def game_page(game_id):

    game = mongo.db.games.find_one({"_id": ObjectId(game_id)})
    return render_template("game_page.html", game=game)


@app.route("/upvote/<game_id>")
def upvote(game_id):
    if "user" not in session:
        return redirect(url_for("login"))

    game = mongo.db.games.find_one({"_id": ObjectId(game_id)})

    if game:
        mongo.db.games.update_one(
            game, {"$set": {"game_rating": int(game["game_rating"]) + 1}})

    return redirect(url_for("game_page", game_id=game_id))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/category/<category_id>")
def category(category_id):
    categories = list(mongo.db.categories.find())
    games = list(mongo.db.games.find())
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("category.html", categories=categories, games=games, category=category)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for('get_categories'))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        edit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, edit)
        flash("Category Updated")
        return redirect(url_for('get_categories'))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Deleted")
    return redirect(url_for('get_categories'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
