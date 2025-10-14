properties([
  pipelineTriggers([githubPush()])
])

pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Branch to deploy')
    }

    environment {
        DATABASE_URL = credentials('attendance-db-url')
        SECRET_KEY = credentials('attendance-secret-key')
        PYTHONPATH = "/tmp/pip-packages/lib/python3.9/site-packages"
    }

    stages {
        stage('Checkout') {
            steps {
                sh 'git clone https://github.com/vodaassure/attendance_system.git .'
            }
        }

        stage('Build') {
            steps {
                sh 'ls -la'
                sh 'pip install --no-cache-dir --prefix=/tmp/pip-packages -r requirements.txt'
                sh 'pip install --no-cache-dir --prefix=/tmp/pip-packages pytest'
            }
        }

        stage('Test') {
            steps {
                sh '''
                    export PYTHONPATH=/tmp/pip-packages
                    pip install --target=/tmp/pip-packages pytest
                    python3.10 -m pytest tests/
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                    if (params.BRANCH_NAME == 'main') {
                        sh 'docker compose build'
                        sh 'docker compose up -d'
                    } else if (params.BRANCH_NAME == 'staging') {
                        sh 'docker compose -f docker-compose.staging.yml build'
                        sh 'docker compose -f docker-compose.staging.yml up -d'
                    } else {
                        echo "No deployment configured for branch: ${params.BRANCH_NAME}"
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
