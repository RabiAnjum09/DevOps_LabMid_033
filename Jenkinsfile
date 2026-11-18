pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'fa23-bds-033-ml:latest'
        CONTAINER_NAME = 'fa23-bds-033-api'
        APP_PORT = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME} .
                    docker run --rm \
                        -v "$WORKSPACE/artifacts:/app/artifacts" \
                        ${IMAGE_NAME} \
                        python train.py
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                        -v "$WORKSPACE:/app" \
                        -w /app \
                        ${IMAGE_NAME} \
                        sh -c "pip install pytest && pytest -v"
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${APP_PORT}:8000 \
                        -v "$WORKSPACE/artifacts:/app/artifacts" \
                        ${IMAGE_NAME}

                    sleep 5
                    curl --fail http://localhost:${APP_PORT}/health
                '''
            }
        }
    }
}
