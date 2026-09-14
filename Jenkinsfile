pipeline {
  agent any
  environment {
    AWS_REGION='ap-south-1'
    ECR_REPOSITORY='taskflow'
    EC2_INSTANCE_ID='i-xxxxxxxxxxxxxxxxx'
    AWS_ACCOUNT_ID='123456789012'
    ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    IMAGE_TAG="${GIT_COMMIT}"
  }
  stages {
    stage('Checkout'){steps{checkout scm}}
    stage('Test'){steps{sh 'python3 -m compileall app'}}
    stage('Build'){steps{sh 'docker build -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} .'}}
    stage('Push to ECR'){
      steps{
        withAWS(credentials:'aws-jenkins-role',region:"${AWS_REGION}"){
          sh '''aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}'''
        }
      }
    }
    stage('Deploy via SSM'){
      steps{
        withAWS(credentials:'aws-jenkins-role',region:"${AWS_REGION}"){
          sh '''aws ssm send-command --instance-ids ${EC2_INSTANCE_ID} --document-name AWS-RunShellScript --parameters commands="[\\"cd /opt/taskflow\\",\\"export IMAGE_TAG=${IMAGE_TAG}\\",\\"./scripts/deploy.sh\\"]" --comment "Jenkins TaskFlow deployment ${IMAGE_TAG}"'''
        }
      }
    }
  }
  post { success {echo 'Deployment completed.'} failure {echo 'Deployment failed.'} }
}
