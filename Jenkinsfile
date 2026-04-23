pipeline {
    agent any
    
    triggers {
        githubPush()
    }
    environment {
        SITE_NAME  = "django-polls"
        WEB_ROOT   = "/var/www/django-polls"
        NGINX_CONF = "/etc/nginx/sites-available/django-polls"
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
                    echo "Checking required project files..."
                    test -f polls/templates/polls/detail.html
                    test -f polls/templates/polls/index.html
                    test -f polls/templates/polls/multi_vote.html
                    test -f polls/templates/polls/results.html
                    test -f polls/templates/polls/results_select.html
                    test -f polls/static/polls/style.css
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
                    sudo apt install -y nginx
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
        stage('Deploy Website Files') {
            steps {
                sh '''
                    set -e
                    rm -rf "$WEB_ROOT"/*
                    cp polls/templates/polls/detail.html "$WEB_ROOT"/
                    cp polls/templates/polls/index.html "$WEB_ROOT"/
                    cp polls/templates/polls/multi_vote.html "$WEB_ROOT"/
                    cp polls/templates/polls/results.html "$WEB_ROOT"/
                    cp polls/templates/polls/results_select.html "$WEB_ROOT"/
                    cp polls/static/polls/style.css "$WEB_ROOT"/
                    [ -f polls/static/polls/Background.png ] && cp polls/static/polls/Background.png "$WEB_ROOT"/ || true
                    echo "Deployed files:"
                    ls -la "$WEB_ROOT"
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
    root $WEB_ROOT;
    index index.html;
    location / {
        try_files \\$uri \\$uri/ =404;
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
