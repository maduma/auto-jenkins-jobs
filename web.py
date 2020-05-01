from flask import Flask, request
import autojj
import gitlab_client
import jenkins_client
import settings

logger = settings.get_logger(__name__)

app = Flask(__name__)


# to test
@app.route('/event', methods=['POST'])
def event():
    if not jenkins_client.is_jenkins_online():
        msg = 'Jenkins is offline'
        logger.error(msg)
        return msg, 503

    if request.is_json and request.headers.get('X-Gitlab-Event') == 'System Hook':
        event = request.get_json()
        return autojj.process_event(event)
    else:
        msg = "Can only process valid Gitlab System Hook"
        logger.info(msg)
        return msg, 200


# to test
@app.route('/health', methods=['GET'])
def health():
    jenkins_status = jenkins_client.is_jenkins_online()
    gitlab_status = gitlab_client.is_gitlab_online()

    if jenkins_status['status'] == 'online' and gitlab_status['status'] == 'online':
        return {
            'status': 'online',
            'version': settings.AUTOJJ_VERSION,
            'jenkins': jenkins_status,
            'gitlab': gitlab_status,
            }
    else:
        return {
            'status': 'degraded',
            'version': settings.AUTOJJ_VERSION,
            'jenkins': jenkins_status,
            'gitlab': gitlab_status
            }
