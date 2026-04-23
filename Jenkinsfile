pipeline {
    agent any
    
    triggers {
        githubPush()
    }

    environment {
        SITE_NAME  = "django-polls"
        WEB_ROOT   = "/var/www/django-polls"
        NGINX_CONF = "/etc/nginx/sites-available/django-polls"
        REPO_URL   = "https://github.com/Judee554/django-polls-app.git"
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                git url: "${REPO_URL}", branch: 'main'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    set -e
                    sudo apt update
                    sudo apt install -y python3-pip python3-venv nginx
                '''
            }
        }

        stage('Setup Django App') {
            steps {
                sh '''
                    set -e

                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    python manage.py migrate
                    python manage.py collectstatic --noinput
                '''
            }
        }

        stage('Prepare Web Directory') {
            steps {
                sh '''
                    set -e
                    sudo mkdir -p "$WEB_ROOT"
                    sudo chown -R jenkins:jenkins "$WEB_ROOT"
                '''
            }
        }

        stage('Configure Nginx') {
            steps {
                sh '''
                    set -e

                    sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location /static/ {
        root $WEB_ROOT;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
    }
}
EOF

                    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/django-polls
                    sudo rm -f /etc/nginx/sites-enabled/default

                    sudo nginx -t
                '''
            }
        }

        stage('Start Django Server') {
            steps {
                sh '''
                    set -e

                    pkill -f "manage.py runserver" || true

                    . venv/bin/activate
                    BUILD_ID=dontKillMe nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
                '''
            }
        }

        stage('Start Nginx') {
            steps {
                sh '''
                    set -e
                    sudo systemctl enable nginx
                    sudo systemctl restart nginx
                '''
            }
        }

        stage('Test Site') {
            steps {
                sh '''
                    set -e
                    curl -I http://localhost
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Your Django site is live via Nginx (port 80)'
        }
        failure {
            echo 'FAILURE: Check Jenkins logs'
        }
    }
}
