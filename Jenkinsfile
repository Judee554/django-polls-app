pipeline {
    agent any
    
    triggers {
        githubPush()
    }

    environment {
        APP_DIR = "/home/ubuntu/django-polls-app"
        VENV_DIR = "/home/ubuntu/venv"
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

        stage('Setup Python Environment') {
            steps {
                sh '''
                    set -e

                    sudo apt update
                    sudo apt install -y python3-pip python3-venv

                    python3 -m venv $VENV_DIR
                    source $VENV_DIR/bin/activate

                    pip install --upgrade pip
                    pip install django gunicorn
                '''
            }
        }

        stage('Prepare App Directory') {
            steps {
                sh '''
                    set -e

                    rm -rf $APP_DIR
                    mkdir -p $APP_DIR
                    cp -r * $APP_DIR
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                sh '''
                    set -e
                    source $VENV_DIR/bin/activate
                    cd $APP_DIR

                    python manage.py migrate
                '''
            }
        }

        stage('Run Django App') {
            steps {
                sh '''
                    set -e
                    source $VENV_DIR/bin/activate
                    cd $APP_DIR

                    pkill gunicorn || true

                    nohup gunicorn mysite.wsgi:application \
                        --bind 0.0.0.0:8000 &
                '''
            }
        }

        stage('Test App') {
            steps {
                sh '''
                    set -e
                    curl -I http://localhost:8000
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful.'
            echo 'Visit: http://YOUR_EC2_PUBLIC_IP:8000'
        }
        failure {
            echo 'Deployment failed. Check Jenkins logs.'
        }
    }
}