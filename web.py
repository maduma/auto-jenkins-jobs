from flask import Flask, request
import autojj
import jenkins_client

import time
import os

VERSION = os.environ.get('AUTOJJ_VERSION', 'unknown')

app = Flask(__name__)

@app.route('/autojj/event', methods=['POST'])
def event():
    is_gitlab_system_event = request.headers.get('X-Gitlab-Event') == 'System Hook'
    if is_gitlab_system_event and request.is_json and jenkins_client.is_jenkins_online():
        event = request.get_json()
        return autojj.process_event(event)
    else:
        return {'description': "Can only process Gitlab 'repository_update' system hook"}, 404

@app.route('/autojj/health', methods=['GET'])
def health():
    jenkins_status = jenkins_client.is_jenkins_online()
    if jenkins_status:
        return {'status': 'pass', 'version': VERSION, 'jenkins': jenkins_status}
    else:
        return {'status': 'No connection to Jenkins', 'version': VERSION, 'jenkins': 'unknown'}, 503