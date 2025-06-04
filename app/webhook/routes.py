from flask import Blueprint, jsonify, request, abort
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

def format_utc_timestamp(ts_str):
    dt = parser.isoparse(ts_str)
    dt = dt.astimezone(dtime.timezone.utc)
    return dt.strftime("%-d %B %Y - %-I:%M %p UTC")

@webhook.route('/receiver', methods=["POST"])
def receiver():
    # Verify signature
    verify_signature()

    event_type = request.headers.get('X-GitHub-Event', 'ping')
    payload = request.json

    if event_type == "push":
        author = payload.get("pusher", {}).get("name", "Unknown")
        branch = payload.get("ref", "").split("/")[-1]
        timestamp = payload.get("head_commit", {}).get("timestamp")
        if timestamp:
            timestamp = format_utc_timestamp(timestamp)
        print(f'"{author}" pushed to "{branch}" on {timestamp}')
    
    elif event_type == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        author = pr.get("user", {}).get("login", "Unknown")
        from_branch = pr.get("head", {}).get("ref")
        to_branch = pr.get("base", {}).get("ref")
        timestamp = pr.get("created_at") if action == "opened" else pr.get("merged_at")

        if timestamp:
            timestamp = format_utc_timestamp(timestamp)

        if action == "opened":
            print(f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}')
        elif action == "closed" and pr.get("merged"):
            print(f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {timestamp}')

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