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

## Solution:

The following statement provies a brief overview of the technical architecture. The solution is split into two parts. The first part covers infrastructure as code (IaC) and the second part covers the CI/CD pipeline. 

# Infrastructure as Code:

The mission statement states that the initial configuration was manually setup and our goal is to capture this configuration with Infrastructure as Code. This allows the DevOps team to deploy infrastructure with the push of a button, version control all infrastructure changes and prevent future outages. This solution deploys the following resources:

- VPC, Internet Gateway, Public Subnet, Route Table, Security Group, Ingress/Egress Rules & EC2 Instance.

Steps to replicate:

*Note: These steps can be run from your local/development machine.*

- Install Terraform
- Install awscli
- Log into AWS Console and create Access Keys (Only recommended for local machine. If you run a CI/CD tool like CircleCI/Jenkins on a dedicated EC2, please attach an AWS IAM role with permissions to provision the above listed resources.)
- Clone this repository and change directories to the Terraform folder.
- Run the following commands to deploy your infrastructure:

      	>  terraform init
        >  terraform plan
        >  terraform apply

![alt text](Benchsci-Arch.png)
