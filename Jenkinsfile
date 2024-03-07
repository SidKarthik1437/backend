pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('django-backend', '-f Dockerfile.backend .')
                }
            }
        }
        
        stage('Run Migrations') {
            steps {
                script {
                    docker.image('django-backend').inside {
                        sh 'python manage.py migrate'
                    }
                }
            }
        }
        stage('Create Admin Group') {
            steps {
                script {
                    docker.image('django-backend').inside {
                        sh 'python manage.py create_groups'
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    kubernetesDeploy(
                        configs: 'nexa-server-deployment.yaml',
                        kubeconfigId: 'mykubeconfig'
                    )
                }
            }
        }
    }
}