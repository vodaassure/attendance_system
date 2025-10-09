pipeline {
    agent {
        docker {
            image 'python:3.9'
        }
    }

    options {
        skipDefaultCheckout(true) // Prevent Jenkins from auto-checking out code
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
               // deleteDir() // Clean workspace before cloning
                // If repo is public, this works. If private, use withCredentials block.
                sh 'git clone https://github.com/vodaassure/attendance_system.git .'
            }
        }

        stage('Build') {
            steps {
                sh 'ls -la' // Debug: list files to confirm requirements.txt is present
             // sh 'pip install --no-cache-dir -r requirements.txt'
                sh 'pip install --no-cache-dir --prefix=/tmp/pip-packages -r requirements.txt'
		sh 'pip install --no-cache-dir --prefix=/tmp/pip-packages pytest'
		
            }
        }

        stage('Test') {
            steps {
                sh '''
                    export HOME=/tmp
                    pip install --user pytest
                    python -m pytest tests/
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
