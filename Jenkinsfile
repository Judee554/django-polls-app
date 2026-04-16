pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Judee554/django-polls-app.git', branch: 'main'
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    set -e
                    python3 -m venv venv || true
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Migrate DB') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate
                    python manage.py migrate
                    python manage.py collectstatic --noinput
                '''
            }
        }

        stage('Run Server') {
            steps {
                sh '''
                    set -e

                    pkill -f "manage.py runserver" || true
                    screen -S django_server -X quit || true

                    screen -dmS django_server bash -c '
                        source venv/bin/activate
                        python manage.py runserver 0.0.0.0:8000
                    '

                    sleep 10
                    sudo ss -tulpn | grep 8000 || true
                    screen -ls || true
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful.'
            echo 'Open your EC2 public IP with :8000'
        }
        failure {
            echo 'Deployment failed. Check the Jenkins console output.'
        }
    }
}