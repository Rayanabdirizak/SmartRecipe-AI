from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # Relationships
    favorites = db.relationship(
        "Favorite",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    meal_plans = db.relationship(
        "MealPlan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class Favorite(db.Model):

    __tablename__ = "favorites"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    recipe_name = db.Column(
        db.String(255),
        nullable=False
    )

    recipe_content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )


class RecipeHistory(db.Model):

    __tablename__ = "recipe_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    recipe_name = db.Column(
        db.String(255),
        nullable=False
    )

    recipe_content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<RecipeHistory {self.recipe_name}>"


class MealPlan(db.Model):

    __tablename__ = "meal_plans"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    day = db.Column(
        db.String(20),
        nullable=False
    )

    meal_name = db.Column(
        db.String(200),
        nullable=False
    )

    meal_type = db.Column(
        db.String(50),
        nullable=False
    )

    calories = db.Column(
        db.Integer
    )

    meal_time = db.Column(
        db.String(20)
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<MealPlan {self.day} - {self.meal_name}>"