from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook
import urllib.parse
import os

username = urllib.parse.quote_plus(os.environ.get("MONGO_USERNAME"))
password = urllib.parse.quote_plus(os.environ.get("MONGO_PASSWORD"))

# Creating our flask app
def create_app():
    app = Flask(__name__)

    # Configure MongoDB Atlas URI
    app.config["MONGO_URI"] = (
        f"mongodb+srv://{username}:{password}@cluster0.0cjmawe.mongodb.net/"
        "?retryWrites=true&w=majority&appName=Cluster0"
    )

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(webhook)

    return app