from flask import Blueprint, jsonify, request

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    payload = request.json
    print(f"Received event: {event_type}")
    print(payload)

    return jsonify({'status': 'received', 'event': event_type}), 200

@webhook.route('/', methods=["GET"])
def home():
    print("Home GET request")
    return 'GitHub Webhook Receiver is running!', 200