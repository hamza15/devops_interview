# devops_interview
This is a hands-on assessment of Infrastructure-as-Code (IaC), CI/CD, and public cloud providers. You may use GCP or AWS as the platform of your choice; you may use `gcloud deployment-manager`, `aws cloudformation`, or `terraform` command-line interface tools. Please do not spend more than 2 hours on this task. You're not expected to setup your own personal cloud account, but there should be enough configuration details so that deploying to a real cloud environment will theoretically work. Be prepared to justify your design.

## Setup:
1. Fork this repo into your own Github account
2. Add user `tonybenchsci` to your forked repo with read access
3. Setup a [free CircleCI accout](https://circleci.com/docs/2.0/first-steps/) and hook up your repo

## Background:
A simple Flask webserver that displays "Hello World from BenchSci!" runs on a Virtual Machine on the cloud. The VM that runs it has several firewall rules associated. The firewall rules are:
- Allow all egress
- Deny all ingress, but allow:
```
TCP Ports 80, 443 from everywhere on the internet
ICMP (ping) from  everywhere on the internet
TCP Port 22 from 104.154.0.0/15 (GOOGLE LLC)
Allow all tcp/udp internal traffic within the VPC
```

## The problem:
The above cloud-native application was manually configured using Web console UIs, and it was accidently deleted by a junior developer. None of the cloud firewall rules were captured in IaC, and neither is the VM configuration. Your assignment is to create the cloud resources in configuration files, and setup CI/CD to create/update the rules based on code changes in the master branch. This would allow arbitrary deploys of the application stack, resilient to incidents. It also allows a team of DevOps engineers to collaborate on new infrastructure definitions.

## Requirements:
- Complete `./circle/config.yml` file that installs CLI tools as needed, configures auth, performs basic sanity tests, and deploys resources.
- Configuration file(s) that define a VPC network that the VM lives in, Firewall rules / Security groups, and a single VM
- (Theoretically deployed) VM runs the python webserver defined in `app.py` on startup and any restarts
- (Theoretically deployed) Working public IP address to see "Hello World from BenchSci!" in a web browser
- Basic Documentation (README.md) and architecture diagram
- Avoid: Unnecessary abstractions in the form of configuration templates and/or modules

# Solution:

The following statement provides a brief overview of the technical architecture. The solution is split into two parts. The first part covers infrastructure as code (IaC) and the second part covers the CI/CD pipeline. 

## Infrastructure as Code:

The mission statement states that the initial configuration was manually setup and our goal is to capture this configuration with Infrastructure as Code. This allows the DevOps team to deploy infrastructure with the push of a button, version control all infrastructure changes and prevent future outages. This solution deploys the following resources:

- VPC, Internet Gateway, Public Subnet, Route Table, Security Group, Ingress/Egress Rules & EC2 Instance.

Steps to replicate:

*Note: These steps can be run from your local/development machine.*

- Install Terraform
- Install awscli
- Log into AWS Console and create Access Keys (Only recommended for local machine. If you run a CI/CD tool like CircleCI/Jenkins on a dedicated EC2, please attach an AWS IAM role with permissions to provision the above listed resources.)
- Run *aws configure* at your terminal to setup your aws environment variables. 
- Clone this repository and change directories to the Terraform folder.
- Run the following commands to deploy your infrastructure:

        >  terraform init
        >  terraform plan
        >  terraform apply

Note: Since the mission statement didn't require the DevOps tools like CircleCI, AWS CodeDeploy etc abstracted, unnecessary abstractions were avoided. Please note that in order to use AWS CodeDeploy, and S3 as a source repository for revisions of your application you do require AWS IAM roles to be created for AWS CodeDeploy, AWS EC2 and S3 Bucket Policies. The details and steps are covered at https://docs.aws.amazon.com/codedeploy/latest/userguide/getting-started-codedeploy.html

*PS: If you would like to ssh into your EC2 and check configurations, a Key value with the name "Docker" has been entered into main.tf. You can replace this with the name of the Key Pair you would like to associate with your EC2 and use it to SSH in. You would have to change SSH security group rules to allow SSH access, since our permissions don't allow it.*

## CI/CD

The mission statement states CircleCI as a requirement for the build and deployment of a simple Hello World application to a VM on the cloud. The solution looks for a commit in the master branch which serves as a triger to start our CI/CD pipeline. After installing dependencies from the requirements.txt file, it runs a unit test against our Flask application. This test looks for a 200 OK status code when our application is started and also conducts a sanity test to confirm "Hello World from Benchsci!" is produced. Two reports are generated as a result of our unit tests. The deploy jobs installs dependencies to run aws cli commands, packages our source code, pushes it to S3 as a Zip, and calls AWS CodeDeploy to deploy that revision to our EC2 instance. 

*Note: To authorize resource deployments from CircleCI to AWS, please configure AWS Access Keys in your CircleCI project. If you are using a dedicated CircleCI server, you should use IAM Roles instead of Access Keys. Also, add an environment variable on your CircleCI project for the default AWS region closest to you.*

Steps to replicate:

- Fork this repository.
- Sign up for CircleCI and authenticate with Github to allow access to this repository.
- Add environment variable in CircleCI
- Create an S3 bucket to store code revisions. (Create a bucket policy to allow CircleCI to access this bucket)
- Navigate to AWS CodeDeploy in the UI amd create an Application, Deployment Group, IAM Role for AWS CodeDeploy and select your EC2 Tag as your deployment target. These steps can also be done via CLI or captured with Terraform in a repository you maintain for all your DevOps tools shared across your organization.)
- Once you are finished, you are ready to test. The appspec.yml file in our config takes care of copying the revision of our source code to our EC2 and runs scripts from inside the Script folder to start and stop our application during deployment.

*Note: AWS CodeDeploy requires an agent running on your EC2, which in our case is already done via a user script passed to our EC2 at launch. This user script covers installation of basic tools and application requirements like pip and Flask.*

Finally, make a change in your configuration and trigger the CI/CD pipeline. A new revision of your application should be visible at the Public-IP/hello endpoint on your browser. :triumph:


# Design Strategy:

The design strategy can be covered in two parts. The first one covers a detailed overview of Infrastructure design and considerations made to deem this design appropriate for our mission. The second part follows a similar pattern in explaining reasons, limitations and preferences that lead to the design of our CI/CD pipeline.

## Infrastructure Design:

As stated in the Infrastructure as Code section, the idea behind the design was to automate infrastructure deployments in order to avoid manual mishaps. The resources required for our design were listed in the mission statement. 

Our solution tries to oversimplify the process of infrastructure automation. As listed in the ‘Requirements’ section, the idea was to avoid unnecessary abstractions by configuring modules. The main.tf file that is used to provision our infrastructure was designed to be readable and obvious. 

In an ideal case, the Terraform folder would be hosted in its own repository inside Github. The main reason behind that design would be that infrastructure is provisioned for multiple services/applications in most organizations. As the complexity for your environment grows beyond just provisioning infrastructure for a single application, we notice that resources such as VPC, Subnets, Internet Gateways, Route tables, Security Groups, and many others are shared across multiple applications, environments and in some cases (Google Cloud) even across regions. Sourcing infrastructure from its own repository allows us to build upon our current terraform scripts and often provision multiple versions (SIT, UAT, PROD) of our infrastructure. It also allows for version control and deploying it via a CI/CD pipeline.

Our mission simulates an MVP/Proof of Concept project where the idea might be to deliver an MVP at a low cost. The simplicity of our design and avoiding unnecessary abstractions allow for us to deliver infrastructure within the 2 hour window. 

## CI/CD Design:

The CI/CD design was inspired by the mission statement requirements. A simple Hello World application was provided with the idea that a commit to master would trigger our CircleCI pipeline. This pipeline would in turn build and then deploy our application to a Virtual Machine running on the cloud. 

Our design process starts with a simple workflow inside the config.yml file which runs our build and deploy jobs. The build process runs against a python image which installs basic tools to build our Flask application and run a simple unit test to confirm proper functionality of our application. The unit tests looks for a 200 OK when the Flask application is started and confirms that Hello World text returned by our application is correct. It also generates two reports for these tests, which allow for observability into our code breaking our build. This allows for checks in place which would make sure breaking changes don’t make it to the deploy phase. Our workflow also requires the build phase to finish before deploy phase kicks in. 

One build phase is successful, deploy phase starts with an install of awscli. The awscli allows us to run commands against S3 and AWS Codedeploy and in turn deploy our application an AWS EC2 instance. After installing zip, we zip our source code and tag it with a revision ID. This zipped file is pushed to an S3 bucket and deployed via AWS CodeDeploy to our EC2 instance.

*Note: In order to run awscli commands certain environment variable were set in place to allow for a proper configuration. These variables are as follows:*

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION

Although not mentioned in the mission statement, our design involved AWS CodeDeploy and S3. When considering deployment methods we had three main options to consider. First method was a manual deployment via a transfer of source code (scp) and then a running a script to stop the old revision and start our new revision. Secondly, we had the option of using AWS CodeDeploy  via CircleCI orbs to deliver our application to our infrastructure. Third and our choice for this mission was using AWS CodeDeploy cli command with S3.

The reason behind our design had a few considerations. Our first consideration was that S3 allowed for artifacts to be stored safely in a repository where their lifecycle could be managed. In an ideal design we often see artifactory as a source of truth for build artifacts that allow for CI/CD pipelines to deliver your source code to multiple environments (SIT, UAT & PROD). In our case S3 would allow for revisions to be managed and in future scenarios be deployed across multiple environments. This allows for artifacts to be built once and then shared across multiple environments without the need to build them again. 

Our second consideration for the use of AWS CodeDeploy was observability and cost. AWS CodeDeploy does not charge for the pull and push of deployments to our AWS EC2 instance. It does however provide complete observability of over the deployment process. The AWS CodeDeploy agent running on our AWS EC2 instance runs health checks on our EC2 instance and allows for safe deployments. The appsepec.yml file allows us to create a very clear and simple method to deploy a revision to our application and most importantly, revert to an older version in case of failure. The rollback feature makes it a strong contender for our design. 

Our design chose to avoid manual deployments because they often involve using ssh to run a deploy script at your target instance. SSH keys should often be rotated and pose an unnecessary security risk. Our appspec.yml deployment method allows for simplicity and readability in our config.yml script.

AWS CodeDeploy orb and our AWS CodeDeploy cli command provide the same functionality with an S3 bucket in place. Our design chose to provide observability via cli commands which could easily be abstracted via aws-codedeploy orb.


![alt text](Benchsci-Arch.png)
