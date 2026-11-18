pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'rabia09/fa23-bds-033-ml'
        CONTAINER_NAME = 'fa23-bds-033-api'
        APP_PORT = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.COMMIT_AUTHOR_EMAIL = sh(
                        script: 'git log -1 --format=%ae',
                        returnStdout: true
                    ).trim()

                    if (!env.COMMIT_AUTHOR_EMAIL.contains('@')) {
                        error('Could not determine commit author email')
                    }

                    echo "Build notification recipient: ${env.COMMIT_AUTHOR_EMAIL}"
                }
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    mkdir -p "$WORKSPACE/artifacts"

                    docker build \
                        -t ${IMAGE_NAME}:latest \
                        -t ${IMAGE_NAME}:${BUILD_NUMBER} .

                    docker run --rm \
                        -e GIT_COMMIT="$GIT_COMMIT" \
                        -v "$WORKSPACE/artifacts:/app/artifacts" \
                        ${IMAGE_NAME}:latest \
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
                        ${IMAGE_NAME}:latest \
                        sh -c "pip install pytest && pytest -v"
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            -u "$DOCKERHUB_USER" --password-stdin

                        docker push ${IMAGE_NAME}:latest
                        docker push ${IMAGE_NAME}:${BUILD_NUMBER}

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker pull ${IMAGE_NAME}:latest

                    docker rm -f ${CONTAINER_NAME} || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --restart unless-stopped \
                        -p ${APP_PORT}:8000 \
                        -v "$WORKSPACE/artifacts:/app/artifacts" \
                        ${IMAGE_NAME}:latest

                    sleep 5
                    curl --fail http://localhost:${APP_PORT}/health
                    curl --fail http://localhost:${APP_PORT}/metrics
                '''
            }
        }
    }

    post {
        success {
            emailext(
                to: "${env.COMMIT_AUTHOR_EMAIL}",
                subject: "FA23-BDS-033 - Build ${env.BUILD_NUMBER} SUCCESS",
                body: """Hello,

Your commit-triggered ML retraining pipeline completed successfully.

Student ID: FA23-BDS-033
Build: ${env.BUILD_NUMBER}
Commit: ${env.GIT_COMMIT}
Docker image: ${env.IMAGE_NAME}:${env.BUILD_NUMBER}
API metrics endpoint: port 8000 (/metrics)

The model was trained, tested, published, and deployed.

"""
            )
        }

        failure {
            emailext(
                to: "${env.COMMIT_AUTHOR_EMAIL}",
                subject: "FA23-BDS-033 - Build ${env.BUILD_NUMBER} FAILED",
                body: """Hello,

The ML retraining pipeline failed.

Student ID: FA23-BDS-033
Build: ${env.BUILD_NUMBER}
Commit: ${env.GIT_COMMIT}

Please check the Jenkins console output for details.
"""
            )
        }
    }
}
