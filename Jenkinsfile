pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        IMAGE_NAME = "django-polls-app"
        CONTAINER_NAME = "django-polls-container"
        HOST_PORT = "8000"
        CONTAINER_PORT = "8000"
    }

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Judee554/django-polls-app.git'
            }
        }

        stage('Verify Project Files') {
            steps {
                sh '''
                    set -e
                    test -f manage.py
                    test -f requirements.txt
                    test -d polls
                    test -d mysite
                    test -f Dockerfile
                    ls -la
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    sudo docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Stop Old Container') {
            steps {
                sh '''
                    set +e
                    sudo docker stop $CONTAINER_NAME
                    sudo docker rm $CONTAINER_NAME
                    set -e
                '''
            }
        }

        stage('Run New Container') {
            steps {
                sh '''
                    set -e
                    sudo docker run -d \
                        --name $CONTAINER_NAME \
                        -p $HOST_PORT:$CONTAINER_PORT \
                        $IMAGE_NAME
                '''
            }
        }

        stage('Test Container') {
            steps {
                sh '''
                    set -e
                    sleep 5
                    curl -I http://127.0.0.1:8000
                '''
            }
        }
    }

    post {
        success {
            echo 'Docker deployment successful.'
        }
        failure {
            echo 'Docker deployment failed. Check Jenkins console output.'
        }
    }
}