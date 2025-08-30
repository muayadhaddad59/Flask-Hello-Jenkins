pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      args '-u root'
      reuseNode true
    }
  }

  options {
    skipDefaultCheckout(true)
    timestamps()
  }

  environment {
    FLASK_PORT = '5001'
    PYTHONPATH = "${WORKSPACE}"              // fix python imports for tests
    NOTIFY = 'muayadhaddad653@gmail.com'     // change if you want
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
          apt-get update -y
          apt-get install -y --no-install-recommends curl git
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Commit metadata') {
      steps {
        sh '''
          set -eux
          echo "Last commit:"
          git --no-pager log -1 --pretty=format:'%h %an <%ae> %s' || true
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
          # wait for app to be ready
          for i in $(seq 1 40); do
            curl -fsS "http://localhost:${FLASK_PORT}/health" && break
            sleep 0.25
          done
          # quick homepage fetch
          curl -fsS "http://localhost:${FLASK_PORT}/" | head -n 5
          kill $APP_PID || true
        '''
      }
    }
  }

  post {
    success {
      mail to: "${env.NOTIFY}",
           subject: "[SUCCESS] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
           body: "Build succeeded. Details: ${env.BUILD_URL}"
    }
    failure {
      mail to: "${env.NOTIFY}",
           subject: "[FAILURE] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
           body: "Build failed. Logs: ${env.BUILD_URL}"
    }
  }
}
