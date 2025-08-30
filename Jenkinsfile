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
    // Change this to your email(s), or omit and use default recipients from system config
    NOTIFY_TO = 'you@example.com'
  }

  // If you installed the GitHub plugin, this enables webhook-triggered builds too.
  // Remove if you prefer configuring triggers in the UI.
  triggers {
    githubPush()      // or comment this and use Poll SCM in the UI
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git --no-pager log -1 --pretty=format:"%h %an %ae %s"'
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
        // Gather commit metadata for the email
        def sha   = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        def msg   = sh(returnStdout: true, script: 'git log -1 --pretty=%s').trim()
        def author= sh(returnStdout: true, script: 'git log -1 --pretty=%an').trim()
        def email = sh(returnStdout: true, script: 'git log -1 --pretty=%ae').trim()
        def branch= sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
        def url   = "${env.BUILD_URL}"

        emailext(
          to: "${env.NOTIFY_TO}",
          subject: "[SUCCESS] ${env.JOB_NAME} #${env.BUILD_NUMBER} on ${branch} (${sha})",
          body: """
            <h3>✅ Build Succeeded</h3>
            <p><b>Job:</b> ${env.JOB_NAME} #${env.BUILD_NUMBER}</p>
            <p><b>Branch:</b> ${branch}<br/>
               <b>Commit:</b> ${sha}<br/>
               <b>Author:</b> ${author} &lt;${email}&gt;<br/>
               <b>Message:</b> ${msg}</p>
            <p><a href="${url}">Open build in Jenkins</a></p>
          """,
          mimeType: 'text/html'
        )
      }
    }

    failure {
      script {
        def url = "${env.BUILD_URL}"
        emailext(
          to: "${env.NOTIFY_TO}",
          subject: "[FAILURE] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
          body: """
            <h3>❌ Build Failed</h3>
            <p><b>Job:</b> ${env.JOB_NAME} #${env.BUILD_NUMBER}</p>
            <p>Check the console log for details:</p>
            <p><a href="${url}">Open build in Jenkins</a></p>
          """,
          mimeType: 'text/html'
        )
      }
    }

    // Only email when status changes (e.g., broken → fixed, fixed → broken)
    changed {
      script {
        def url = "${env.BUILD_URL}"
        emailext(
          to: "${env.NOTIFY_TO}",
          subject: "[CHANGED] ${env.JOB_NAME} #${env.BUILD_NUMBER} is now ${currentBuild.currentResult}",
          body: """
            <h3>ℹ️ Build Result Changed</h3>
            <p>New result: <b>${currentBuild.currentResult}</b></p>
            <p><a href="${url}">Open build in Jenkins</a></p>
          """,
          mimeType: 'text/html'
        )
      }
    }
  }
}
