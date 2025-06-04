from flask import Blueprint, jsonify, request, abort
import os
import hmac
import hashlib

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
    # Verify signature
    verify_signature()

    event_type = request.headers.get('X-GitHub-Event', 'ping')
    payload = request.json

    print(f"Received event: {event_type}")
    print(payload)

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