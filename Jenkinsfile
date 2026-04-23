pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        SITE_NAME  = "django-polls"
        WEB_ROOT   = "/var/www/django-polls"
        NGINX_CONF = "/etc/nginx/sites-available/django-polls"
        APP_DIR    = "/var/lib/jenkins/workspace/JudeeJ_COMP314_Exercise4"
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
                    test -d polls
                    test -d mysite
                    echo "Required files found."
                    ls -la
                '''
            }
        }

        stage('Install Dependencies') {
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

        stage('Setup Django App') {
            steps {
                sh '''
                    set -e

                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    python3 manage.py migrate --noinput
                    python3 manage.py collectstatic --noinput || true

                    if [ -d /var/www/django-polls-app/static ]; then
                        rm -rf "$WEB_ROOT/static/"*
                        cp -r /var/www/django-polls-app/static/* "$WEB_ROOT/static/" || true
                    fi

                    echo "Static files copied."
                    ls -la "$WEB_ROOT/static" || true
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
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
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

                    nohup bash -c "cd $APP_DIR && . venv/bin/activate && python3 manage.py runserver 0.0.0.0:8000" > django.log 2>&1 &

                    sleep 5
                    pgrep -f "manage.py runserver" > /dev/null
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
                    curl -I http://127.0.0.1:8000
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
