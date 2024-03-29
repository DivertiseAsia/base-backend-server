# Deployment Setup

## Required Environment Dependent Variables

1. AWS_LOGS_GROUP
2. CPU_RESERVATION
3. MEMORY_RESERVATION
4. START_CMD
5. RDS_HOST
6. RDS_USERNAME
7. RDS_PASSWORD
8. RDS_DB_NAME
9. DJANGO_SETTINGS_MODULE
10. DJANGO_SECRET_KEY
11. AWS_S3_ACCESS_KEY_ID
12. AWS_S3_SECRET_ACCESS_KEY
13. AWS_SES_ACCESS_KEY_ID
14. AWS_SES_SECRET_ACCESS_KEY
15. SUPER_ADMIN_PASS
16. VERSION_TAG

## Required Variables

1. AWS_DEFAULT_REGION
2. AWS_SES_REGION_NAME
3. PROJECT_NAME
4. AWS_ACCESS_KEY_ID
5. AWS_SECRET_ACCESS_KEY
6. REPOSITORY_URL

## Django Required Setting Variables

On production these setting variables should not be `[""]` or `["*"]`
for security reason

1. [ALLOWED_HOSTS](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts)
2. [CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES](https://github.com/adamchainz/django-cors-headers#configuration)

# AWS Environment Setup

## Deployment Users and Permissions

1. Todo

## Setting up the Cloud

1. Create a VPC named "project"-"env"-vpc with default settings using VPC and more
   1. Ensure public vpc subnets in "edit subnet settings" has **Enable auto-assign public IPv4 addressInfo** checked
2. Create a RDS instance named "project"-"env"-db
   1. Template free (Single DB - Burstable t3 micro)
   2. Drop storage down to 20GB
   3. Select your VPC
   4. Create new VPC security group rds-"project"-"env"-sg
   5. Pick a username eg pu-"project"-"env and password - write both down and put it in the bitbucket deployment variables.
   6. Select Password & IAM database
   7. Create. Wait then grab url. Put host, database name, username, and password into bitbucket deployment variables.
3. Create keypair eg "project"-"env"-kp changing to .pem type. Save this pem file cause otherwise it's gone forever
4. Create ecs cluster
   1. Name it "project"-"env"
   2. If staging / dev you can choose **spot** otherwise suggest **demand**; lowest price is fine for **spot**
   3. For staging choose **t3-micro**
   4. Select the keypair you made in the previous step so you can remote into the instances later
   5. Choose your vpc and subnet from step 1
   6. New Security Grouop
   7. Create
5. Create loggroup
   1. Name /ecs/"project"-"env"
   2. Retention 1 week
6. Attempt deploy
   1. This should test everything up to this point and you should have a task definition added called "project"-:env":1 under your cluster.
7. Create service from the cluster page
   1. Launch type - ec2
   2. Choose cluster from step 4
   3. Service name - "project"-service
   4. Tasks should be at least 1
   5. Change minimum healthy to 50%
   6. Hit create and go to Step 2 (Configure Network)
   7. Choose Application Load Balancer
   8. Create an application load balancer named "project"-"env"-lb. Note if it has a warning it won't work later, and you'll have to fix it. Choose your public subnets
   9. Scheme should be Internet-facing
   10. Select IPV4
   11. Select your vpc "project"-"env"-vpc
   12. Create a new security group "project"-"env"-lb-sg
       1. Select your vpc
       2. Create
   13. Create a target group
       1. Instance target type
       2. Name it "project"-"env"-tg
       3. Leave as port 80, your vpc (should be selected already), and http1
       4. Change checks both to 3 and timeout to 60 seconds, interval to 120, and success codes to 200,301,499
   14. Now you can select your target group and security group on the Application Load Balancer. Save it. Go back to the service tab from Step 6
   15. Select your load balancer and hit next step
   16. You just need to setup port 80 and hit create. If it fails hit back and hit save again
8. Update the service
   1. This will end up trying to deploy it out to an instance
   2. We still need to fix up all the ports so things can talk properly.
9. Update security groups
   1. Allow inbound Postgres port to rds from your ecs group
   2. Allow http and https for ipv4 and ipv6 to load balancer group
   3. Allow all ports from load balancer to ecs group
10. Add Route53 A Record for api to load balancer

## Add S3 bucket permission for public folder:

1. Make sure bucket name does not include any "."'s
2. Click on bucket -> Permissions -> Block public access (bucket settings) Press Edit
3. Untick everything
4. Go to bucket policy -> Edit:
5. Use this (assuming staging)

```
{
    "Version": "2012-10-17",
    "Id": "PreventHotlinking",
    "Statement": [
        {
            "Sid": "AllowGetRequestsFromYourDomain",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::BUCKET_NAME/public/*",
            "Condition": {
                "StringLike": {
                    "aws:Referer": [
                        "http://localhost:8080/*",
                        "https://localhost:8080/*",
                        "http://staging.APP.com/*",
                        "https://staging.APP.com/*"
                    ]
                }
            }
        }
    ]
}
```

6. Save
7. Change s3 public permissions to use everything but leave "Block public and cross-account access ... through any public ...." unticked
8. Save changes

## Set up server HTTPS:

### Generate SSL Certificate

1.  Go to AWS Certificate Manager -> Certificates
2.  Request
3.  Request a public certificate
4.  Enter domain name, DNS validation, RSA 2048
5.  Request

### Set up load balancer to allow HTTPS

1.  Go to load balancer
2.  Add listener
3.  Select HTTPS
4.  Forward to app-env-tg
5.  Select your SSL certificate from step 1
6.  Add

## Allow access through HTTPS only:

1. Go to load balancer
2. Select load balancer -> add listener
3. Add HTTP:80 port and redirect action to HTTPS:443

## FAQ:

1. Where to check server logs - Go to ECS -> Clusters -> your cluster name -> Tasks -> select your task -> logs - or go to CloudWatch -> log groups -> /ecs/
2. When cannot access server website: - Check if ECS task is running/recent - Check Cloudwatch loggroup logs
3. When agent failed to connect:

- Press on app-service in ECS -> Deployments and Events -> Events
- "service app-service was unable to place a task because no container instance met all of its requirements. The closest matching container-instance <container-id> doesn't have the agent connected. For more information, see the Troubleshooting section of the Amazon ECS Developer Guide."
- Go to EC2 instance -> Select -> Instance state -> Reboot instance
- Go to service -> select -> update
