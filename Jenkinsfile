pipeline {
    agent any

    environment {
        EC2_USER    = "ubuntu"
        EC2_HOST    = "3.138.190.82"
        CRED_ID     = "ec2-ssh-private-key"
        PROJECT_DIR = "/home/ubuntu/django-polls-app"
        REPO_URL    = "https://github.com/Judee554/django-polls-app.git"
    }

    stages {
        stage('Clean Deploy & Start Server') {
            steps {
                script {
                    sshagent([CRED_ID]) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} "
                            
                            sudo apt-get update && sudo apt-get install -y python3-venv python3-pip git

                            sudo fuser -k 8000/tcp || true

                            sudo rm -rf ${PROJECT_DIR}
                            cd /home/ubuntu
                            git clone ${REPO_URL} django-polls-app

                            cd ${PROJECT_DIR}
                            python3 -m venv venv
                            . venv/bin/activate

                            pip install --upgrade pip
                            pip install -r requirements.txt

                            python3 manage.py migrate --noinput
                            python3 manage.py collectstatic --noinput || true

                            BUILD_ID=dontKillMe nohup python3 manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &

                            sleep 2
                            echo 'Server started at http://${EC2_HOST}:8000'
                        "
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Your site is live at http://3.134.89.131:8000"
        }
        failure {
            echo "FAILURE: Check Jenkins console output for errors."
        }
    }
}
