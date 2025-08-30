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
    PYTHONPATH = "${WORKSPACE}"
    NOTIFY_TO = 'muayadhaddad653@gmail.com'   // change if needed
  }

  stages {

    stage('Checkout') {
      steps {
        // checkout happens inside the container
        checkout scm
        sh 'python -V && ls -la'
      }
    }

    stage('Install deps') {
      steps {
        sh '''
          set -eux
          apt-get update -y
          # need curl for smoke test, git for commit metadata
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
          git --no-pager log -1 --pretty=format:'%h %an <%ae> %s'
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
    success {
      script {
        // Only works once SMTP is configured/reachable
        emailext(
          to: "${env.NOTIFY_TO}",
          subject: "[SUCCESS] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
          body: "<p>Build succeeded. <a href='${env.BUILD_URL}'>Open</a></p>",
          mimeType: 'text/html'
        )
      }
    }
    failure {
      script {
        emailext(
          to: "${env.NOTIFY_TO}",
          subject: "[FAILURE] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
          body: "<p>Build failed. <a href='${env.BUILD_URL}'>Open logs</a></p>",
          mimeType: 'text/html'
        )
      }
    }
  }
}
