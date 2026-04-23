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
        APP_DIR    = "/var/lib/jenkins/workspace/JudeeJ_COMP314_Exercise4"
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
                    python manage.py collectstatic --noinput || true
                '''
            }
        }

        stage('Prepare Static Directory') {
            steps {
                sh '''
                    set -e
                    sudo mkdir -p "$WEB_ROOT/static"
                    [ -d staticfiles ] && sudo cp -r staticfiles/* "$WEB_ROOT/static/" || true
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
        alias $WEB_ROOT/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
    }
}
EOF
                    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/django-polls
                    sudo rm -f /etc/nginx/sites-enabled/default
                    sudo nginx -t
                    sudo systemctl enable nginx
                    sudo systemctl restart nginx
                '''
            }
        }

        stage('Start Django in Background') {
            steps {
                sh '''
                    set -e
                    pkill -f "manage.py runserver" || true
                    nohup bash -c "cd $APP_DIR && . venv/bin/activate && python manage.py runserver 0.0.0.0:8000" > django.log 2>&1 &
                    sleep 5
                    pgrep -f "manage.py runserver" > /dev/null
                '''
            }
        }

        stage('Test App') {
            steps {
                sh '''
                    set -e
                    curl -I http://127.0.0.1:8000
                    curl -I http://localhost
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful.'
            echo 'Open your EC2 public IP in a browser.'
        }
        failure {
            echo 'Deployment failed. Check Jenkins console output.'
        }
    }
}
