pipeline {
    agent any

    environment {
        EC2_USER = "ubuntu"  // Or ubuntu, depending on your AMI
        EC2_HOST = "44.197.180.64" //(MODIFY)
        EC2_KEY = credentials('ec2-ssh-private-key')  // Jenkins credential with SSH private key (MODIFY)
        PROJECT_DIR = "/home/ubuntu/pythonprojects/django_polls"  // Path to your Django app (MODIFY)
        
    }

    //triggers {
      //  githubPush()  // Enables webhook triggering
    //}
    
    stages {
        stage('Update Code on EC2') {
            steps {
                script {
                    // Use SSH to run commands on the EC2 instance
                    sshagent (credentials: ['ec2-ssh-private-key']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            cd ${PROJECT_DIR}
                            git pull origin main
                            python3 -m venv comp314
                            source comp314/bin/activate
                            python3 -m pip install -r requirements.txt
                        '
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Code updated and app restarted successfully on EC2!"
        }
        failure {
            echo "Deployment failed."
        }
    }
}
