from flask import Flask, request, jsonify, abort
import autojj

import time
import os

app = Flask(__name__)

@app.route('/autojj/event', methods=['POST'])
def event():
    is_gitlab_system_event = request.headers.get('X-Gitlab-Event') == 'System Hook'
    if is_gitlab_system_event and request.is_json:
        event = request.get_json()
        return autojj.process_event(event)
    else:
        return abort(404, description="Can only process Gitlab 'repository_update' system hook")

@app.route('/autojj/health', methods=['GET'])
def health():
    version = os.environ.get('VERSION', 'unknown')
    return jsonify({'status': 'pass', 'version': version, 'jenkins': 'online'})