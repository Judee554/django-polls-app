pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        WEB_ROOT = "/var/www/django-polls-app"
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

        stage('Verify Project Files') {
            steps {
                sh '''
                    set -e
                    echo "Checking required Django project files..."

                    test -f manage.py
                    test -d mysite
                    test -d polls
                    test -f requirements.txt

                    echo "Required files found."
                    ls -la
                '''
            }
        }

        stage('Install Python') {
            steps {
                sh '''
                    set -e
                    sudo pkill -f apt || true
                    sudo rm -f /var/lib/apt/lists/lock
                    sudo rm -f /var/cache/apt/archives/lock
                    sudo rm -f /var/lib/dpkg/lock-frontend
                    sudo rm -f /var/lib/dpkg/lock
                    sudo dpkg --configure -a || true
                    sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
                    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-venv
                '''
            }
        }

        stage('Create Web Root') {
            steps {
                sh '''
                    set -e
                    sudo mkdir -p "$WEB_ROOT"
                    sudo chown -R jenkins:jenkins "$WEB_ROOT"
                '''
            }
        }

        stage('Deploy Project Files') {
            steps {
                sh '''
                    set -e
                    rm -rf "$WEB_ROOT"/*
                    cp -r * "$WEB_ROOT"/

                    echo "Deployed files:"
                    ls -la "$WEB_ROOT"
                '''
            }
        }

        stage('Set Up Virtual Environment') {
            steps {
                sh '''
                    set -e
                    cd "$WEB_ROOT"

                    rm -rf venv
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Django Setup') {
            steps {
                sh '''
                    set -e
                    cd "$WEB_ROOT"
                    . venv/bin/activate

                    python manage.py migrate
                    python manage.py collectstatic --noinput
                '''
            }
        }

        stage('Start Django Server') {
            steps {
                sh '''
                    set -e
                    cd "$WEB_ROOT"

                    pkill -f "manage.py runserver" || true

                    nohup setsid "$WEB_ROOT"/venv/bin/python manage.py runserver 0.0.0.0:8000 --noreload > django.log 2>&1 < /dev/null &

                    sleep 10

                    echo "Checking if server is running..."
                    sudo ss -tulpn | grep 8000 || true

                    echo "Last logs:"
                    tail -n 20 django.log || true

                    curl -I http://127.0.0.1:8000
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful.'
            echo 'Open: http://18.188.39.93:8000'
        }
        failure {
            echo 'Deployment failed. Check the Jenkins console output.'
        }
    }
}