
from flask import Flask, render_template, request, jsonify
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask_login import LoginManager
from models import db, User, MealPlan, Favorite, RecipeHistory
from werkzeug.security import generate_password_hash
from flask import redirect, flash, url_for
from werkzeug.utils import secure_filename
import uuid
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)


app.config["SECRET_KEY"] = "your-secret-key"

app.config["UPLOAD_FOLDER"] = "static/uploads"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()

login_manager.login_view = "login"

login_manager.init_app(app)

app.config["SECRET_KEY"] = "your-secret-key"

recipes = [
    {"title":"Cheesy Pizza","category":"Italian","ingredients":["cheese","flour","tomato","oregano"],"image":"pizza.jpg"},
    {"title":"Classic Burger","category":"Fast Food","ingredients":["beef","cheese","bread","lettuce"],"image":"burger.jpg"},
    {"title":"Creamy Pasta","category":"Italian","ingredients":["pasta","cream","garlic"],"image":"pasta.jpg"},
    {"title":"Grilled Chicken","category":"Healthy","ingredients":["chicken","garlic","pepper"],"image":"chicken.jpg"},
]

@app.route("/")
def home():
    query=request.args.get("search","").lower()
    if query:
        words=[w.strip() for w in query.split(",")]
        results=[r for r in recipes if any(w in r["ingredients"] for w in words)]
    else:
        results=recipes
    return render_template("index.html",recipes=results,search=query)

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash(
                f"Welcome back, {user.username}!",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/recipe")
def recipe(): return render_template("recipe.html")

@app.route("/add-recipe")
def add_recipe(): return render_template("add_recipe.html")

@app.route("/favorites")
@login_required
def favorites():

    user_favorites = Favorite.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Favorite.created_at.desc()
    ).all()

    return render_template(
        "favorites.html",
        favorites=user_favorites
    )


@app.route("/delete-favorite/<int:favorite_id>", methods=["POST"])
@login_required
def delete_favorite(favorite_id):

    favorite = Favorite.query.filter_by(
        id=favorite_id,
        user_id=current_user.id
    ).first()

    if favorite:

        db.session.delete(favorite)
        db.session.commit()

        flash("Favorite removed.", "success")

    return redirect(url_for("favorites"))

from models import MealPlan

@app.route("/planner")
@login_required
def planner():

    user_meals = MealPlan.query.filter_by(
        user_id=current_user.id
    ).all()

    meals = {}

    for meal in user_meals:

        meals[meal.day] = meal

    return render_template(
        "planner.html",
        meals=meals
    )


@app.route("/save-meal", methods=["POST"])
@login_required
def save_meal():

    day = request.form.get("day")
    meal_name = request.form.get("meal_name")
    meal_type = request.form.get("meal_type")
    calories = request.form.get("calories")
    meal_time = request.form.get("meal_time")
    notes = request.form.get("notes")

    if not day or not meal_name:
        return jsonify({
            "success": False,
            "error": "Day and Meal Name are required."
        })

    # Check if a meal already exists for this day
    meal = MealPlan.query.filter_by(
        user_id=current_user.id,
        day=day
    ).first()

    if meal:

        meal.meal_name = meal_name
        meal.meal_type = meal_type
        meal.calories = calories
        meal.meal_time = meal_time
        meal.notes = notes

    else:

        meal = MealPlan(
            day=day,
            meal_name=meal_name,
            meal_type=meal_type,
            calories=calories,
            meal_time=meal_time,
            notes=notes,
            user_id=current_user.id
        )

        db.session.add(meal)

    db.session.commit()

    return jsonify({
        "success": True
    })


@app.route("/delete-meal/<day>", methods=["POST"])
@login_required
def delete_meal(day):

    meal = MealPlan.query.filter_by(
        user_id=current_user.id,
        day=day
    ).first()

    if meal:
        db.session.delete(meal)
        db.session.commit()

    return jsonify({
        "success": True
    })

@app.route("/get-meal/<day>")
@login_required
def get_meal(day):

    meal = MealPlan.query.filter_by(
        user_id=current_user.id,
        day=day
    ).first()

    if meal is None:
        return jsonify({
            "success": False
        })

    return jsonify({
        "success": True,
        "meal": {
            "meal_name": meal.meal_name,
            "meal_type": meal.meal_type,
            "calories": meal.calories,
            "meal_time": meal.meal_time,
            "notes": meal.notes
        }
    })


@app.route("/shopping")
def shopping(): return render_template("shopping.html")

@app.route("/dashboard")
@login_required
def dashboard():

    total_recipes = len(recipes)

    total_meal_plans = MealPlan.query.filter_by(
        user_id=current_user.id
    ).count()

    # Temporary until Favorites and Shopping
    # are moved into the database
    total_favorites = 0
    total_shopping = 0

    return render_template(
        "dashboard.html",
        user=current_user,
        total_recipes=total_recipes,
        total_favorites=total_favorites,
        total_meal_plans=total_meal_plans,
        total_shopping=total_shopping
    )
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))


@app.route("/history")
@login_required
def history():

    history = RecipeHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        RecipeHistory.created_at.desc()
    ).all()

    return render_template(
        "recipe_history.html",
        history=history
    )


@app.route("/ai")
def ai(): return render_template("ai_recipe.html")

@app.route("/generate-recipe", methods=["POST"])
def generate_recipe():

    ingredients = request.form.get("ingredients", "").strip()

    if not ingredients:
        return jsonify({"error": "Please enter some ingredients."}), 400

    prompt = f"""
    You are a professional chef.
    Create a delicious recipe using these ingredients:
    {ingredients}

    Include:
    - Recipe Name
    - Ingredients
    - Instructions
    - Cooking Time
    - Tips
    """

    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        recipe_text = response.text

        # Save history only if the user is logged in
        if current_user.is_authenticated:

            recipe = RecipeHistory(
                recipe_name=ingredients.title(),
                recipe_content=recipe_text,
                user_id=current_user.id
            )

            db.session.add(recipe)
            db.session.commit()

        return jsonify({
            "recipe": recipe_text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


    
@app.route("/save-favorite", methods=["POST"])
@login_required
def save_favorite():

    recipe_name = request.form.get("recipe_name")
    recipe_content = request.form.get("recipe_content")

    if not recipe_name or not recipe_content:

        return jsonify({
            "success": False,
            "message": "Missing recipe."
        })

    favorite = Favorite(
        recipe_name=recipe_name,
        recipe_content=recipe_content,
        user_id=current_user.id
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Recipe saved!"
    })

@app.route("/download-pdf",methods=["POST"])
def download_pdf():
    recipe=request.form.get("recipe","")
    os.makedirs("static/pdfs",exist_ok=True)
    filename="static/pdfs/recipe.pdf"
    doc=SimpleDocTemplate(filename)
    styles=getSampleStyleSheet()
    story=[Paragraph(line,styles["BodyText"]) for line in recipe.split("\n")]
    doc.build(story)
    return jsonify({"url":"/static/pdfs/recipe.pdf"})

@app.route("/analyze-nutrition",methods=["POST"])
def analyze_nutrition():
    recipe=request.form.get("recipe","").strip()
    if not recipe:
        return jsonify({"error":"Recipe is empty."}),400
    prompt=f"""Analyze this recipe nutritionally:\n{recipe}"""
    try:
        response=client.models.generate_content(model="gemini-flash-lite-latest",contents=prompt)
        return jsonify({"nutrition":response.text})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/contact")
def contact():
    return render_template("contact.html")
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        try:

            msg = MIMEMultipart()

            msg["From"] = EMAIL_ADDRESS
            msg["To"] = EMAIL_ADDRESS
            msg["Subject"] = f"SmartRecipe AI - {subject}"

            body = f"""
New Contact Message

Name: {name}

Email: {email}

Subject: {subject}

Message:

{message}
"""

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            server.send_message(msg)

            server.quit()

            flash(
                "✅ Your message has been sent successfully!",
                "success"
            )

        except Exception as e:

            print("=" * 60)
            print("EMAIL ERROR:")
            print(repr(e))
            print("=" * 60)

            flash(
                str(e),
                "danger"
            )

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/profile")
@login_required
def profile():

    total_recipes = len(recipes)

    total_meal_plans = MealPlan.query.filter_by(
        user_id=current_user.id
    ).count()

    total_favorites = 0

    return render_template(
        "profile.html",
        user=current_user,
        total_recipes=total_recipes,
        total_meal_plans=total_meal_plans,
        total_favorites=total_favorites
    )

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    if request.method == "POST":

        current_user.username = request.form["username"]
        current_user.email = request.form["email"]

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    return render_template("edit_profile.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("change_password"))

        current_user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("profile"))

    return render_template("change_password.html")


import os

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )