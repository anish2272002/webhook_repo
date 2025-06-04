from flask import Blueprint, jsonify, request, abort
from app.extensions import mongo
import os
import hmac
import hashlib
import datetime as dtime
from dateutil import parser

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

def verify_signature(secret_env_name="GITHUB_SECRET"):
    secret = os.environ.get(secret_env_name,"my-secret-token")
    if not secret:
        abort(500, 'Webhook secret not configured')

    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        abort(400, 'Missing signature header')

    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        abort(400, 'Only sha256 is supported')

    mac = hmac.new(secret.encode(), msg=request.data, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        abort(403, 'Invalid signature')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    verify_signature()

    event_type = request.headers.get('X-GitHub-Event', 'ping')
    payload = request.json

    record = {
        "request_id": None,
        "author": None,
        "action": None,
        "from_branch": None,
        "to_branch": None,
        "timestamp": None
    }

    if event_type == "push":
        record["author"] = payload.get("pusher", {}).get("name", "Unknown")
        record["action"] = "PUSH"
        record["to_branch"] = payload.get("ref", "").split("/")[-1]
        record["request_id"] = payload.get("head_commit", {}).get("id")
        record["timestamp"] = payload.get("head_commit", {}).get("timestamp")

    elif event_type == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})

        record["author"] = pr.get("user", {}).get("login", "Unknown")
        record["from_branch"] = pr.get("head", {}).get("ref")
        record["to_branch"] = pr.get("base", {}).get("ref")
        record["request_id"] = str(pr.get("id"))
        record["timestamp"] = pr.get("created_at") if action == "opened" else pr.get("merged_at")

        if action == "opened":
            record["action"] = "PULL_REQUEST"
        elif action == "closed" and pr.get("merged"):
            record["action"] = "MERGE"

    # Normalize timestamp to UTC ISO format
    if record["timestamp"]:
        dt = parser.isoparse(record["timestamp"]).astimezone(dtime.timezone.utc)
        record["timestamp"] = dt.isoformat()

    # Drop None values to avoid invalid MongoDB fields
    clean_record = {k: v for k, v in record.items() if v is not None}

    # Insert into MongoDB Atlas
    mongo.db.github_events.insert_one(clean_record)

    return jsonify({'status': 'received', 'event': event_type}), 200

@webhook.route('/', methods=["GET"])
def home():
    print("Home GET request")
    return 'GitHub Webhook Receiver is running!', 200

@webhook.route('/debug-secret')
def debug_secret():
    return jsonify({
        'GITHUB_SECRET': os.environ.get('GITHUB_SECRET', 'Not set')
    })