pipeline {
    agent any

    environment {
        a = 1
        b = True
        c = asdfasdf
        RE_RAISE_UNKNOWN_EXCEPTIONS = False
    }

    stages {
        stage('build') {
            steps {
                sh "/usr/local/miniconda3/envs/py39/bin/python -m venv venv"
                sh "venv/bin/pip install --upgrade pip"
                sh "venv/bin/pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple"
                sh "venv/bin/pip install -r requirements.txt"
            }

            post {
                failure {
                    dingtalk (
                        robot: 'ae354bc2-26a2-4236-af96-c877f1a372e8',
                        type: 'LINK',
                        text: [
                            'django_json_api_utils 安装环境依赖出现错误，点击查看详情'
                        ],
                        messageUrl: 'http://114.116.222.153:12312/blue/organizations/jenkins/django_json_api_utils/activity'
                    )
                }
              }

        }
        stage('lint') {
            steps {
                echo 'check format..'
                sh 'venv/bin/pip install -q flake8'
                sh 'venv/bin/flake8 --max-line-length=120 djapi'
                sh 'venv/bin/flake8 --max-line-length=120 tests'
            }
            post {
                failure {
                    dingtalk (
                        robot: 'ae354bc2-26a2-4236-af96-c877f1a372e8',
                        type: 'LINK',
                        text: [
                            'django_json_api_utils 代码格式检查出现错误，点击查看详情'
                        ],
                        messageUrl: 'http://114.116.222.153:12312/blue/organizations/jenkins/django_json_api_utils/activity'
                    )
                }
              }

        }
        stage('test') {
            steps {
                echo 'test....'
                sh 'venv/bin/pytest --cov-report=html:cov_html --cov=djapi --cov=tests'
            }
            post {
                success {
                    dingtalk (
                        robot: 'ae354bc2-26a2-4236-af96-c877f1a372e8',
                        type: 'LINK',
                        text: [
                            'django_json_api_utils 成功构建，点击查看详情'
                        ],
                        messageUrl: 'http://114.116.222.153:12312/blue/organizations/jenkins/django_json_api_utils/activity'
                    )
                }
                failure {
                    dingtalk (
                        robot: 'ae354bc2-26a2-4236-af96-c877f1a372e8',
                        type: 'LINK',
                        text: [
                            'django_json_api_utils 构建测试出现错误，点击查看详情'
                        ],
                        messageUrl: 'http://114.116.222.153:12312/blue/organizations/jenkins/django_json_api_utils/activity'
                    )
                }
            }
        }
        stage('Clean Workspace') {
         steps {

          sh("ls -al ${env.WORKSPACE}")
          deleteDir()  // clean up current work directory
          sh("ls -al ${env.WORKSPACE}")

         }
      }
    }
}
