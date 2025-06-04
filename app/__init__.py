from flask import Flask
from .extensions import mongo
from app.webhook.routes import webhook


# Creating our flask app
def create_app():
    app = Flask(__name__)

    # Configure MongoDB Atlas URI
    app.config["MONGO_URI"] = (
        "mongodb+srv://anish2272002:Anish@2272002@cluster0.0cjmawe.mongodb.net/"
        "?retryWrites=true&w=majority&appName=Cluster0"
    )

    # Initialize extensions
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(webhook)

    return app