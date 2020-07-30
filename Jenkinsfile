#!groovy

def server = Artifactory.server "rep.msk.mts.ru"
server.setBypassProxy(true)

String git_tag
String git_branch
String git_commit

Boolean isMaster = false
Boolean isDev = true
Boolean isRelease = false

String version

node('bdbuilder04') {
    environment {
        COMPOSE_PROJECT_NAME = "${env.JOB_NAME}-${env.BUILD_ID}"
    }

    try {
        gitlabBuilds(builds: ["Build test images", "Run unit tests", "Check coverage", "Pylint", "Sonar Scan", "Retrieve Sonar Results", "Deploy test images", "Build pip package", "Building documentation", "Publishing package to Artifactory", "Build and push nginx docs images"]) {
            stage('Checkout') {
                def scmVars = checkout scm
                git_tag = "${scmVars.GIT_TAG}".trim()
                if (git_tag == 'null' || git_tag == '') {
                    git_tag = null
                }
                git_branch = scmVars.GIT_BRANCH.replace('origin/', '').replace('feature/', '').trim()
                git_commit = scmVars.GIT_COMMIT

                println(git_tag)
                println(git_branch)
                println(git_commit)

                sh script: """
                    mkdir -p ./reports/junit
                    touch ./reports/pylint.txt
                """
            }

            isMaster  = git_branch == 'master'
            isDev     = git_branch == 'dev'
            isRelease = isMaster && git_tag
            version   = git_tag

            String testTag = isMaster ? 'test' : 'dev-test'

            List pythonVersions = ['2.7', '3.6', '3.7']

            List test_images = []

            stage('Build test images') {
                gitlabCommitStatus('Build test images') {
                    pythonVersions.each{ def pythonVersion ->
                        def testTagVersioned = "${testTag}-python${pythonVersion}"

                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    // Fetch cache
                                    cache = docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}").pull()
                                } catch (Exception e) {}

                                test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTagVersioned}", "--build-arg PYTHON_VERSION=${pythonVersion} --force-rm -f Dockerfile.test .")
                            }
                        }
                    }
                    ansiColor('xterm') {
                        withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                            try {
                                // Fetch cache
                                docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").pull()
                            } catch (Exception e) {}

                            test_images << docker.build("docker.rep.msk.mts.ru/mlflow-client:${testTag}", "--force-rm -f Dockerfile.test .")
                        }
                    }
                }
            }

            stage('Run unit tests') {
                gitlabCommitStatus('Run unit tests') {
                    pythonVersions.each{ def pythonVersion ->
                        withEnv(["TAG=${testTag}-python${pythonVersion}"]) {
                            ansiColor('xterm') {
                                sh script: """
                                    docker-compose -f docker-compose.jenkins.yml run --rm mlflow-client-jenkins
                                    docker-compose -f docker-compose.jenkins.yml down
                                """
                            }
                        }
                    }
                }
            }

            stage('Check coverage') {
                gitlabCommitStatus('Check coverage') {
                    docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").inside() {
                        ansiColor('xterm') {
                            sh script: """
                                coverage.sh
                            """
                        }
                    }

                    junit 'reports/junit/*.xml'
                }
            }

            stage('Pylint') {
                gitlabCommitStatus('Pylint') {
                    docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").inside() {
                        ansiColor('xterm') {
                            sh script: """
                                python -m pylint .mlflow_client -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" --exit-zero > reports/pylint.txt
                            """
                        }
                    }
                }
            }

            stage('Sonar Scan') {
                gitlabCommitStatus('Sonar Scan') {
                    withSonarQubeEnv('sonarqube') {
                        withCredentials([string(credentialsId: 'SONAR_DB_PASSWD', variable: 'SONAR_DB_PASSWD')]) {
                        ansiColor('xterm') {
                                //TODO: remove hardcoded URL after DEVOPSMISC-2353
                                sh "/data/sonar-scanner/bin/sonar-scanner -Dsonar.host.url=http://10.72.20.32:9000"
                            }
                        }
                    }
                }
            }

            stage('Retrieve Sonar Results') {
                gitlabCommitStatus('Retrieve Sonar Results') {
                    timeout(time: 15, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }

            stage('Deploy test images') {
                gitlabCommitStatus('Deploy test image') {
                    if (isDev || isRelease) {
                        test_images.each { def image ->
                            ansiColor('xterm') {
                                withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                    image.push()
                                }
                            }
                        }
                    }
                }
            }

            stage('Build pip package') {
                gitlabCommitStatus('Build pip package') {
                    if (isDev || isRelease) {
                        //Build wheels for each version
                        pythonVersions.each{ def pythonVersion ->
                            docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}-python${pythonVersion}").inside() {
                                ansiColor('xterm') {
                                    sh script: """
                                        python setup.py bdist_wheel sdist
                                    """
                                }
                            }
                        }
                    }
                }
            }

            stage ('Building documentation') {
                gitlabCommitStatus('Building documentation') {
                    docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").inside() {
                        try {
                            version = sh script: "python setup.py --version", returnStdout: true
                            version = version.trim()
                        } catch (Exception e) {}
                    }

                    if (isMaster) {
                        docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").inside() {
                            ansiColor('xterm') {
                                sh script: """
                                    cd docs
                                    make html
                                    tar cvzf html-latest.tar.gz -C build/html .
                                """
                            }
                        }

                        if (isRelease) {
                            docker.image("docker.rep.msk.mts.ru/mlflow-client:${testTag}").inside() {
                                ansiColor('xterm') {
                                    sh script: """
                                        cp docs/html-latest.tar.gz docs/html-${version}.tar.gz
                                    """
                                }
                            }
                        }

                        def uploadSpec = '''{
                                "files": [
                                    {
                                        "pattern": "docs/html-*.tar.gz",
                                        "target": "files/mlflow-client-docs/"
                                    }
                                ]
                            }'''

                        def buildInfo = server.upload spec: uploadSpec
                        server.publishBuildInfo buildInfo
                    }
                }
            }

            stage('Publishing package to Artifactory') {
                gitlabCommitStatus('Publishing package to Artifactory') {
                    if (isRelease) {
                        def uploadSpec = '''{
                                "files": [
                                    {
                                        "pattern": "dist/.*(.tar.gz|.whl)",
                                        "target": "pypi-local/mlflow-client/",
                                        "regexp": "true"
                                    }
                                ]
                            }'''

                        def buildInfo = server.upload spec: uploadSpec
                        server.publishBuildInfo buildInfo
                    }
                }
            }

            stage('Build and push nginx docs images') {
                gitlabCommitStatus('Build nginx and push docs images') {
                    if (isMaster) {
                        ansiColor('xterm') {
                            withDockerRegistry([credentialsId: 'tech_jenkins_artifactory', url: 'https://docker.rep.msk.mts.ru']) {
                                try {
                                    // Fetch cache
                                    docker.image("docker.rep.msk.mts.ru/mlflow-client.nginx:latest").pull()
                                } catch (Exception e) {}

                                def docs_image = docker.build("docker.rep.msk.mts.ru/mlflow-client.nginx:latest", "--force-rm -f ./docs/nginx/Dockerfile_nginx .")
                                docs_image.push()

                                if (isRelease){
                                    docs_image.push(version)
                                }
                            }
                        }
                    }
                }
            }
        }
    } finally {
        stage('Cleanup') {
            //Docker is running with root privileges, and Jenkins has no root permissions to delete folders correctly
            //So use a small hack here
            docker.image('platform/python:2.7').inside("-u root") {
                ansiColor('xterm') {
                    sh script: ''' \
                        rm -rf .[A-z0-9]*
                        rm -rf *
                    ''', returnStdout: true
                }
            }
            deleteDir()
        }
    }
}

gitlabCommitStatus(name: 'Deploying the documentation to the nginx server') {
    node('bdbuilder04'){
        stage ('Deploying the documentation') {
            deleteDir()
            checkout scm

            vault_token_cred = 'vault_token_hdp_pipe'
            withCredentials([string(credentialsId: vault_token_cred, variable: 'token')]) {
                ansibleKey = vault("${token}", "platform/ansible/ansible_ssh_key")
                writeFile file: "./docs/ansible.key", text: "${ansibleKey['ansible_ssh_key']}"

                ansiblePlaybook(
                    playbook: './docs/ansible/nginx_deployment.yml',
                    inventory: './docs/ansible/inventory.ini',
                    credentialsId: './docs/ansible.key',
                    extraVars: [
                        target_host: "test_mlflow",
                        docs_version: 'latest'
                    ],
                    extras: '-vv'
                )
            }

            deleteDir()
        }
    }
}