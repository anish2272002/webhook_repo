import os
import urllib.parse
from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook

# Creating our flask app
def create_app():
    app = Flask(__name__)

    # URL encode MongoDB credentials
    username = urllib.parse.quote_plus(os.getenv("MONGO_USERNAME", "your_default_user"))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD", "your_default_pass"))

    mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.0cjmawe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Configure MongoDB Atlas URI
    app.config["MONGO_URI"] = mongo_uri

    # Initialize extensions
    mongo.init_app(app)

    # Test connection
    try:
        mongo.cx.server_info()  # triggers a server call to check connection
        print("MongoDB connection successful")
    except Exception as e:
        print("MongoDB connection failed:", e)

    # Register blueprints
    app.register_blueprint(webhook)

    return app