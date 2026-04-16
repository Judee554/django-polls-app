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
                    nohup setsid venv/bin/python manage.py runserver 0.0.0.0:8000 --noreload > django.log 2>&1 < /dev/null &
                    sleep 10
                    sudo ss -tulpn | grep 8000 || true
                    tail -n 20 django.log || true
                    curl -I http://127.0.0.1:8000 || true
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