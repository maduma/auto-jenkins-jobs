
def registry = 'registry.in.luxair.lu'
def registry_creds_id = 'registry'
def registry_namespace = 'infra'
def python_image = 'python:3.8'

def deploy_env = env.DEPLOY_ENV ?: 'tst'
def registry_url = 'https://' + registry
def git_tag = parseReleaseTag()
def app_name = "$JOB_BASE_NAME"
def app_version = git_tag == 'deploy-only' ? env.DOCKER_IMAGE.split(':').last() : "$git_tag-b$BUILD_ID"
def docker_image = "$registry/" + (env.DOCKER_IMAGE ?: "$registry_namespace/$app_name:$app_version")
def timestamp = new Date().format("yyMMdd_HHmmss")
def tarball = "$app_name-$app_version-$deploy_env-${timestamp}.tar"


pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                sh 'git version'
                sh 'env'
                echo "$git_tag"
            }
        }

        stage('Unit test') {
            agent {
                docker {
                    image python_image
                    args '-v $HOME/.pip-cache:/.cache'
                }
            }
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest -v
                    '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build --build-arg APP_VERSION=$app_version -t $docker_image ."
            }
        }

        stage('Push Docker Image') {
            when {
                beforeAgent true
                expression { env.gitlabBranch }
            }
            steps {
                withDockerRegistry([credentialsId: registry_creds_id, url: registry_url]) {
                    sh "docker push $docker_image"
                }
            }
        }

    }
}

def parseTagName(reference) {
    def matcher = (reference =~ /refs\/tags\/(.+)/)
    if (matcher) {
        return matcher[0][1]
    } else {
        error "Cannot parse Tag! : $reference"
    }
}

def parseReleaseTag() {
    '''
    # Examples of valid version
    v1.0.3
    v1.2.3-sec-23
    v2.3.4-beta
    '''
    def tag = ''
    if (!env.gitlabBranch) {
        env.DEPLOY_ONLY = 'deploy-only '
        tag = 'deploy-only'
        error "deploy-only not yet allowed"
    } else {
        env.DEPLOY_ONLY = ''
        tag = parseTagName(env.gitlabBranch)
        if (! tag =~ /v(\d+\.){2}\d+(-[\w-]+)?/) {
            error "Tag $tag is not a following release convention! (eg. v2.0.2)"
        }
    }
    return tag
}
