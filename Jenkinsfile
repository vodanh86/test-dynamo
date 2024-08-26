pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                ansiColor('xterm') {
                    sh './test_and_dist'
                }
                junit 'test_reports/*.xml'
            }
        }
    }
    post{
        failure {
              slackSend (color: '#FF0000', message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }
        fixed {
              slackSend (color: '#bde133', message: "FIXED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
        }
    }
    triggers {
        cron(env.BRANCH_NAME == 'master' ? '@daily' : '')
    }
}
