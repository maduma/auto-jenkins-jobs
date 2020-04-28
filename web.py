from flask import Flask, request
import autojj
import gitlab_client
import jenkins_client
import settings

app = Flask(__name__)

# to test
@app.route('/event', methods=['POST'])
def event():
    if not jenkins_client.is_jenkins_online():
        return {'description': 'Jenkins not online'}, 503

    is_gitlab_system_event = request.headers.get('X-Gitlab-Event') == 'System Hook'
    if is_gitlab_system_event and request.is_json:
        event = request.get_json()
        return autojj.process_event(event), 200
    else:
        return {'description': "Can only process valid Gitlab System Hook"}, 400

# to test
@app.route('/health', methods=['GET'])
def health():
    jenkins_status = jenkins_client.is_jenkins_online()
    gitlab_status = gitlab_client.is_gitlab_online()
    if jenkins_status['status'] == 'online' and gitlab_status['status'] == 'online':
        return {'status': 'online', 'version': settings.AUTOJJ_VERSION, 'jenkins': jenkins_status, 'gitlab': gitlab_status}
    else:
        return {'status': 'degraded', 'version': settings.AUTOJJ_VERSION, 'jenkins': jenkins_status, 'gitlab': gitlab_status}
