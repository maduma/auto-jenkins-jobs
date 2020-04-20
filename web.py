from flask import Flask, request
import time
import os

import autojj
import jenkins_client
import settings

app = Flask(__name__)

# to test
@app.route('/autojj/event', methods=['POST'])
def event():
    if not jenkins_client.is_jenkins_online():
        return {'description': 'Jenkins not online'}, 503

    is_gitlab_system_event = request.headers.get('X-Gitlab-Event') == 'System Hook'
    if is_gitlab_system_event and request.is_json:
        event = request.get_json()
        return autojj.process_event(event)
    else:
        return {'description': "Can only process valid Gitlab System Hook"}, 400

# to test
@app.route('/autojj/health', methods=['GET'])
def health():
    jenkins_status = jenkins_client.is_jenkins_online()
    if jenkins_status:
        return {'status': 'pass', 'version': settings.AUTOJJ_VERSION, 'jenkins': jenkins_status}
    else:
        return {'status': 'Jenkins not online', 'version': settings.AUTOJJ_VERSION, 'jenkins': 'No connection'}, 503
