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
        stage('Verify Project Files') {
            steps {
                sh '''
                    set -e
                    echo "Checking required project files..."
                    test -f manage.py
                    test -f requirements.txt
                    echo "Required files found."
                    ls -la
                '''
            }
        }
        stage('Install Nginx') {
            steps {
                sh '''
                    set -e
                    sudo apt update
                    sudo apt install -y nginx python3-pip python3-venv
                '''
            }
        }
        stage('Create Web Root') {
            steps {
                sh '''
                    set -e
                    sudo mkdir -p "$WEB_ROOT/static"
                    sudo chown -R jenkins:jenkins "$WEB_ROOT"
                '''
            }
        }
        stage('Deploy Website Files') {
            steps {
                sh '''
                    set -e
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    python3 manage.py migrate
                    python3 manage.py collectstatic --noinput || true
                    rm -rf "$WEB_ROOT/static"/*
                    cp -r staticfiles/* "$WEB_ROOT/static/" 2>/dev/null || true
                    echo "Deployed files:"
                    ls -la "$WEB_ROOT/static"
                '''
            }
        }
        stage('Configure Nginx Site') {
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
                    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/django-polls
                    sudo rm -f /etc/nginx/sites-enabled/default
                    sudo nginx -t
                '''
            }
        }
        stage('Start Nginx') {
            steps {
                sh '''
                    set -e
                    sudo systemctl enable nginx
                    sudo systemctl restart nginx
                    sudo systemctl status nginx --no-pager
                '''
            }
        }
        stage('Test Website Locally') {
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
            echo 'Deployment successful.'
            echo 'Open your EC2 public IP in a browser to view the site.'
        }
        failure {
            echo 'Deployment failed. Check the Jenkins console output.'
        }
    }
}
