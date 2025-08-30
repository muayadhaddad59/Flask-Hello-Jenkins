pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      // run as root so we can apt-get curl for the smoke test
      args '-u root'
      reuseNode true
    }
  }

  // prevent Jenkins' default checkout (which happens before the container starts)
  options {
    skipDefaultCheckout(true)
    timestamps()
  }

  environment {
    FLASK_PORT = '5001'
    // 👇 makes "from app import app" work during pytest
    PYTHONPATH = "${WORKSPACE}"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'python -V && ls -la'
      }
    }

    stage('Install deps') {
      steps {
        sh '''
          set -eux
          apt-get update -y && apt-get install -y --no-install-recommends curl
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Unit tests') {
      steps {
        sh 'pytest -q'
      }
    }

    stage('Smoke test') {
      steps {
        sh '''
          set -eux
          python app.py & APP_PID=$!
          # wait for app to come up
          for i in $(seq 1 40); do
            curl -fsS "http://localhost:${FLASK_PORT}/health" && break
            sleep 0.25
          done
          curl -fsS "http://localhost:${FLASK_PORT}/" | head -n 3
          kill $APP_PID || true
        '''
      }
    }
  }

  post {
    always {
      echo 'Build complete.'
    }
  }
}
