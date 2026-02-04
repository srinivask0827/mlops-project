pipeline {
  agent any

  environment {
    IMAGE_NAME = "ml-api"
    CLUSTER_NAME = "mlops-cluster"
  }

  stages {

    stage("Checkout Code") {
      steps {
        checkout scm
      }
    }

    stage("Build Docker Image") {
      steps {
        bat "docker build -t %IMAGE_NAME%:latest ."
      }
    }

    stage("Load Image into KIND") {
      steps {
        bat "kind load docker-image %IMAGE_NAME%:latest --name %CLUSTER_NAME%"
      }
    }

    stage("Deploy to Kubernetes") {
      steps {
        bat "kubectl apply -f k8s/"
      }
    }

    stage("Restart Deployment") {
      steps {
        bat "kubectl rollout restart deployment ml-api-deployment"
      }
    }

    stage("Verify Rollout") {
      steps {
        bat "kubectl rollout status deployment ml-api-deployment --timeout=120s"
      }
    }
  }
}

