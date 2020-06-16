def git_tag = parseReleaseTag()

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
                    image 'python:3.8'
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
                sh "docker build --build-arg AUTOJJ_VERSION=$git_tag -t registry.in.luxair.lu/infra/autojj:$git_tag ."
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
