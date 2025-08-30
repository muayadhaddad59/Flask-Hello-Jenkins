pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      // run as root to apt-get curl for the smoke test
      args '-u root'
    }
  }

  environment {
    PIP_CACHE_DIR = '.pip-cache'
    FLASK_PORT = '5001'
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        sh 'python --version'
      }
    }

    stage('Install deps') {
      steps {
        sh '''
          apt-get update -y && apt-get install -y --no-install-recommends curl
          python -m pip install --upgrade pip
          pip install -r requirements.txt --cache-dir $PIP_CACHE_DIR
        '''
      }
    }

    stage('Unit tests') {
      steps {
        sh 'pytest -q'
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: '**/pytest*.xml'
        }
      }
    }

    stage('Smoke test') {
      steps {
        sh '''
          python app.py &
          APP_PID=$!
          # wait for app
          for i in $(seq 1 20); do
            curl -fsS "http://localhost:${FLASK_PORT}/health" && break
            sleep 0.5
          done
          echo "Health OK"
          # simple page fetch
          curl -fsS "http://localhost:${FLASK_PORT}/" | head -n 3
          kill $APP_PID || true
        '''
      }
    }
  }

  options {
    timestamps()
  }

  post {
    always {
      echo 'Build complete.'
    }
  }
}
