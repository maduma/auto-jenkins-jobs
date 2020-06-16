def call(Map config = [:]) {

    // default parameters
    def default_deploy_config = [
        tst: [
                [
                    server: 'cicd.in.luxair.lu',
                    service: 'cicd.in.luxair.lu',
                ],
        ],
        acc: [
                [
                    server: 'dmule1a.in.luxair.lu',
                    service: 'dmule1a.in.luxair.lu',
                ],
                [
                    server: 'dmule2a.in.luxair.lu',
                    service: 'dmule2a.in.luxair.lu',
                ],
        ],
        prd: [
                [
                    server: 'dmule1a.in.luxair.lu',
                    service: 'dmule1a.in.luxair.lu',
                ],
                [
                    server: 'dmule2a.in.luxair.lu',
                    service: 'dmule2a.in.luxair.lu',
                ],
        ],
    ]

    def graylog_default_servers = [
        tst: 'grayloga',
        acc: 'grayloga',
        prd: 'graylogp',
    ]

    def registry = config.get('registry','registry.in.luxair.lu')
    def registry_creds_id = config.get('registry_creds_id', 'registry')
    def registry_namespace = config.get('registry_namespace', 'infra')
    def python_image = config.get('python_image', 'python:3.8.2-slim')
    def dockerize_image = config.get('dockerize_image', 'registry.in.luxair.lu/dockerize:0.6.1')
    def deploy_config = config.get('deploy_config', default_deploy_config)
    def deploy_user = config.get('deploy_user', 'root')
    def deploy_creds_id = config.get('deploy_creds_id', 'jenkins_ssh')
    def graylog_servers = config.get('graylog_servers', graylog_default_servers)

    def deploy_env = env.DEPLOY_ENV ?: 'tst'
    def deploy_host0 = "${deploy_config[deploy_env][0]['server']}"
    def service_host0 = "${deploy_config[deploy_env][0]['service']}"
    def deploy_host1 = deploy_env != 'tst' ? "${deploy_config[deploy_env][1]['server']}" : ''
    def service_host1 = deploy_env != 'tst' ? "${deploy_config[deploy_env][1]['service']}" : ''

    def registry_url = 'https://' + registry
    def git_tag = parseReleaseTag()
    def app_name = "$JOB_BASE_NAME"
    def app_version = git_tag == 'deploy-only' ? env.DOCKER_IMAGE.split(':').last() : "$git_tag-b$BUILD_ID"
    def docker_image = "$registry/" + (env.DOCKER_IMAGE ?: "$registry_namespace/$app_name:$app_version")
    def timestamp = new Date().format("yyMMdd_HHmmss")
    def tarball = "$app_name-$app_version-$deploy_env-${timestamp}.tar"

    // get git credentials directly from job configuration
    def git_creds_id = scm.userRemoteConfigs[0].credentialsId

    pipeline {
        agent any
        
        parameters {
            choice(name: 'DEPLOY_ENV', choices: ['tst', 'acc', 'prd'], description: 'Environment where to deploy')
            imageTag(name: 'DOCKER_IMAGE', image: "$registry_namespace/$app_name", registry: registry_url,
                filter: '.*', description: 'Image version to deploy', credentialId: registry_creds_id)
        }

        stages {

            stage('Initialize') {
                steps {
                    updateGitlabCommitStatus name: 'build', state: 'running'
                    script {
                        if (!env.gitlabBranch && !env.DOCKER_IMAGE) {
                            error "Nether started by Gitlab or DOCKER_IMAGE environment set!"
                        }
                        app_id = deployementName(app_name, git_tag)

                        // debug
                        config.each { key, value -> println "$key: $value" }
                    }
                    sh "env | sort"
                }
            }
            
            stage('Checkout and Unit Test') {
                when {
                    beforeAgent true
                    expression { env.gitlabBranch }
                }
                agent {
                    docker {
                        image python_image
                        args '-v $HOME/.pip-cache:/.cache'
                    }
                }
                stages {

                    stage('Checkout') {
                        steps {
                            checkout([
                                $class: 'GitSCM',
                                branches: [[name: git_tag]],
                                extensions: [[$class: 'WipeWorkspace']],
                                userRemoteConfigs: [[credentialsId: git_creds_id, url: "$GIT_URL"]],
                                ])
                        }
                    }

                    stage('Unit Test') {
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

                }
            }

            stage('Build Docker Image') {
                when {
                    beforeAgent true
                    expression { env.gitlabBranch }
                }
                steps {
                    sh """
                        docker build \
                            --pull \
                            --build-arg PYTHON_IMAGE=$python_image \
                            --build-arg APP_VERSION=$app_version \
                            -t $docker_image .
                        """
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

            stage('Release and Deploy') {
                environment {
                    // needed for docker-compose template
                    APP_ID = "$app_id"
                    TRAEFIK_LABEL = "${app_id.replaceAll('\\.', '_')}" // dot (.) is a delimiter for traefik configuration
                    DOCKER_IMAGE = "$docker_image"
                    DEPLOY_ENV = "$deploy_env"
                    DEPLOY_CREDS_ID = "$deploy_creds_id"
                    DEPLOY_USER = "$deploy_user"
                    GRAYLOG_SERVER = "${graylog_servers[deploy_env]}"
                }
                stages {

                    stage('Make Deployment Configuration - node 1') {
                        agent { docker { image dockerize_image } }
                        environment {
                            DEPLOY_HOST = "${deploy_host0}"
                            SERVICE_HOST = "${service_host0}"
                        }
                        steps {
                            docker_compose_release(app_id, deploy_env, tarball)
                            error "stop"
                        }
                    }

                    stage('Deploy Application - node 1') {
                        environment {
                            DEPLOY_HOST = "${deploy_host0}"
                        }
                        steps {
                            ssh_and_deploy(tarball, app_id, deploy_env)
                        }
                    }

                    stage('Test Application - node 1') {
                        steps {
                            heartbeatTest("https://$service_host0/$app_id/health")
                        }
                    }

                    stage('Make Deployment Configuration - node 2') {
                        when {
                            beforeAgent true
                            expression { deploy_env != 'tst' }
                        }
                        agent { docker { image dockerize_image } }
                        environment {
                            DEPLOY_HOST = "${deploy_host1}"
                            SERVICE_HOST = "${service_host1}"
                        }
                        steps {
                            docker_compose_release(app_id, deploy_env, tarball)
                        }
                    }

                    stage('Deploy Application - node 2') {
                        when {
                            beforeAgent true
                            expression { deploy_env != 'tst' }
                        }
                        environment {
                            DEPLOY_HOST = "${deploy_host1}"
                        }
                        steps {
                            ssh_and_deploy(tarball, app_id, deploy_env)
                        }
                    }

                    stage('Test Application node 2') {
                        when {
                            beforeAgent true
                            expression { deploy_env != 'tst' }
                        }
                        steps {
                            heartbeatTest("https://$service_host1/$app_id/health")
                        }
                    }
                }
            }
        }

        post {
            failure {
                updateGitlabCommitStatus name: 'build', state: 'failed'
            }
            success {
                updateGitlabCommitStatus name: 'build', state: 'success'
            }
            always {
                script {
                    manager.addShortText("${env.DEPLOY_ONLY}$app_version $deploy_env")
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
    } else {
        env.DEPLOY_ONLY = ''
        tag = parseTagName(env.gitlabBranch)
        if (! tag =~ /v(\d+\.){2}\d+(-[\w-]+)?/) {
            error "Tag $tag is not a following release convention! (eg. v2.0.2)"
        }
    }
    return tag
}

def copyMissingResources(resources = []) {
    for (filename in resources) {
        if (!fileExists(filename) || isDefaultResource(filename)) {
            println "Copying from resources: ${filename}"
            writeFile file: filename, text: libraryResource(filename)
        }
    }
}

def isDefaultResource(filename) {
    contents = readFile file :filename
    return contents.contains("# JENKINS_DEFAULT #")
}

def sshCmd(cmd) {
    sshagent(["$DEPLOY_CREDS_ID"]) {
        sh "ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST '$cmd'"
    }
}

def scpFile(file, target) {
    sshagent(["$DEPLOY_CREDS_ID"]) {
        sh "scp -o StrictHostKeyChecking=no $file $DEPLOY_USER@$DEPLOY_HOST:$target/"
    }
}

def deployementName(app_name, git_tag) {
    if (git_tag == 'deploy-only') {
        tag_message = ''
    } else {
        tag_message = sh script: "git show -s $git_tag", returnStdout: true
    }
    if (tag_message.contains('UNIQUEBASEPATH')) {
        println "UNIQUEBASEPATH found in tag message"
        env.UNIQUEBASEPATH = "TRUE"
        return "$app_name-$git_tag"
    } else {
        env.UNIQUEBASEPATH = "FALSE"
        return app_name 
    }
}

def heartbeatTest(heartbeatUrl) {
    sh "sleep 60"
    sh "curl -m 5 -s $heartbeatUrl | grep -B1 -A3 '\"pass\"' "
}

def docker_compose_release(app_id, deploy_env, tarball) {
    copyMissingResources(['docker-compose.tmpl.yaml'])
    sh """
        set -ex
        rm -fr $app_id && mkdir $app_id
        dockerize -template docker-compose.tmpl.yaml:$app_id/docker-compose.yaml
        cat $app_id/docker-compose.yaml
        [ -r docker-compose.${deploy_env}.tmpl.yaml ] \
        && dockerize -template docker-compose.${deploy_env}.tmpl.yaml:$app_id/docker-compose.${deploy_env}.yaml \
        && cat $app_id/docker-compose.${deploy_env}.yaml
        echo $tarball > $app_id/.tarball
        [ "$UNIQUEBASEPATH" = "TRUE" ] && touch $app_id/.uniquebasepath
        tar cvf $tarball $app_id
    """
    stash name: 'deployment', includes: tarball
}  

def ssh_and_deploy(tarball, app_id, deploy_env) {
    unstash 'deployment'
    sshCmd "mkdir -p /app/deployments"
    scpFile(tarball, "/app/deployments")
    sshCmd """
        set -x
        cd /app && rm -fr $app_id && tar xvf deployments/$tarball
        cd /app/$app_id
        if  [ -r docker-compose.${deploy_env}.yaml ]; then
            docker-compose -f docker-compose.yaml -f docker-compose.${deploy_env}.yaml up -d
        else
            docker-compose up -d
        fi
    """
}

call()
