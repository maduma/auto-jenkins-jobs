pipeline {
    agent {
        docker { image 'python:3.8' }
    }

    stages {

        stage('Checkout') {
            steps {
                sh 'git version'
            }
        }
    }
}