# 💰 Django Expense Tracker – AWS Cloud Deployment

A web-based Expense Tracker application built using Python and Django. This project demonstrates Django application development and the deployment of a web application on AWS using cloud infrastructure, networking, security, and DevOps concepts.

The application is designed to be deployed on Amazon EC2 inside a custom Amazon VPC. AWS IAM roles are used to provide secure access to Amazon S3 for backup purposes.

---

## 📌 Project Overview

The Expense Tracker application allows users to manage their expenses through a web interface.

The AWS deployment demonstrates how to:

- Create and configure AWS IAM policies and roles
- Build a custom VPC network
- Configure public and private subnets
- Configure an Internet Gateway
- Configure route tables
- Create EC2 instances
- Deploy a Django application on Linux
- Configure Gunicorn as an application server
- Configure Nginx as a reverse proxy
- Use Amazon S3 for backups
- Monitor infrastructure using Amazon CloudWatch

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web application framework |
| SQLite | Database |
| HTML | Frontend structure |
| CSS | Frontend styling |
| Git | Version control |
| GitHub | Source code repository |
| AWS IAM | Access management |
| Amazon VPC | Network infrastructure |
| Amazon EC2 | Application hosting |
| Amazon S3 | Backup storage |
| Gunicorn | Django application server |
| Nginx | Reverse proxy and web server |
| Amazon CloudWatch | Monitoring and logs |
| Linux | Server operating system |

---

# ☁️ AWS Architecture

## Architecture Diagram

```text
                        INTERNET
                           |
                           |
                    Internet Gateway
                           |
                           |
                 Public Route Table
                  0.0.0.0/0 -> IGW
                           |
                           |
                PUBLIC SUBNET 10.0.1.0/24
                           |
                           |
                     EC2 INSTANCE
                   Amazon Linux 2023
                           |
                    Security Group
                     SSH - Port 22
                    HTTP - Port 80
                           |
                           |
                        NGINX
                    Reverse Proxy
                           |
                           |
                       GUNICORN
                    Django Application
                           |
                           |
                       SQLITE DB


                  EC2 IAM INSTANCE ROLE
                           |
                           |
                    IAM PERMISSIONS
                           |
                           |
                       AMAZON S3
                    Backup Storage


                  PRIVATE SUBNET
                  10.0.2.0/24
             Reserved for future resources
```

## AWS Services Used

1. AWS IAM
2. Amazon VPC
3. Subnets
4. Internet Gateway
5. Route Tables
6. Security Groups
7. Amazon EC2
8. Amazon S3
9. Amazon CloudWatch

---

# 1. AWS IAM – Identity and Access Management

## What is IAM?

AWS Identity and Access Management (IAM) is a service that allows us to manage identities, permissions and access to AWS resources.

IAM helps control:

- Who can access AWS resources
- What actions users can perform
- Which AWS resources users or services can access

## IAM Components Used

- IAM Policy
- IAM Role
- EC2 Instance Role

### 1.1 Create a Custom IAM Policy

Navigate to:

```text
AWS Console → IAM → Policies → Create policy
```

Select the JSON editor and create a custom policy for S3 backup access.

Policy name:

```text
ExpenseTracker-S3-Backup-Policy
```

Policy JSON:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListExpenseTrackerBackupBucket",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::expense-tracker-anjal-backup"
        },
        {
            "Sid": "ManageExpenseTrackerBackupObjects",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::expense-tracker-anjal-backup/*"
        }
    ]
}
```

Replace the bucket name if a different S3 bucket name is used.

### Policy Explanation

| Permission | Description |
|---|---|
| `s3:ListBucket` | Lists objects inside the specified bucket |
| `s3:PutObject` | Uploads objects into the bucket |
| `s3:GetObject` | Downloads objects from the bucket |
| `Effect: Allow` | Grants the specified permissions |
| `Resource` | Restricts access to the designated bucket and its objects |

The policy follows the principle of least privilege by granting access only to the required S3 bucket.

### 1.2 Create an IAM Role for EC2

Navigate to:

```text
AWS Console → IAM → Roles → Create role
```

Configuration:

| Setting | Value |
|---|---|
| Trusted entity type | AWS service |
| Service | EC2 |
| Use case | EC2 |
| Role name | ExpenseTracker-EC2-S3-Role |

Attach the custom policy:

```text
ExpenseTracker-S3-Backup-Policy
```

Create the role.

### Why use an IAM Role?

An IAM role allows an EC2 instance to obtain temporary AWS credentials automatically.

Instead of storing permanent access keys on the server, the EC2 instance assumes its assigned IAM role and receives temporary credentials.

Benefits:

- No hardcoded AWS access keys
- Temporary credentials
- Secure access to S3
- Easier credential management
- Reduced risk of credential leakage

---

# 2. Amazon VPC – Virtual Private Cloud

## What is VPC?

Amazon VPC allows us to create an isolated virtual network in AWS.

We can configure:

- IP address ranges
- Subnets
- Route tables
- Internet connectivity
- Network security

## 2.1 Create a VPC

Navigate to:

```text
AWS Console → VPC → Your VPCs → Create VPC
```

Select:

```text
Resources to create: VPC only
```

Configuration:

| Setting | Value |
|---|---|
| Name | ExpenseTracker-VPC |
| IPv4 CIDR | 10.0.0.0/16 |
| IPv6 | No IPv6 CIDR |
| Tenancy | Default |

Click Create VPC.

### What is CIDR?

CIDR stands for Classless Inter-Domain Routing.

It defines the IP address range of a network.

Example:

```text
10.0.0.0/16
```

This VPC provides a private IPv4 address range for our AWS infrastructure.

---

# 3. Create Subnets

A subnet is a smaller network created inside a VPC.

We will create one public subnet for the application server and one private subnet reserved for future infrastructure.

## 3.1 Create Public Subnet

Navigate to:

```text
VPC → Subnets → Create subnet
```

Configuration:

| Setting | Value |
|---|---|
| VPC | ExpenseTracker-VPC |
| Subnet name | ExpenseTracker-Public-Subnet |
| Availability Zone | Select one AZ |
| IPv4 CIDR | 10.0.1.0/24 |

Create the subnet.

### Enable Auto-Assign Public IPv4

Select the public subnet.

Choose:

```text
Actions → Edit subnet settings
```

Enable:

```text
Auto-assign public IPv4 address
```

Save the settings.

The public subnet will host the EC2 application server.

## 3.2 Create Private Subnet

Navigate to:

```text
VPC → Subnets → Create subnet
```

Configuration:

| Setting | Value |
|---|---|
| VPC | ExpenseTracker-VPC |
| Subnet name | ExpenseTracker-Private-Subnet |
| Availability Zone | Same or another AZ |
| IPv4 CIDR | 10.0.2.0/24 |

Create the subnet.

The private subnet is reserved for future resources such as a database server.

Note: We are not launching a database server in the private subnet in the current version.

---

# 4. Create an Internet Gateway

## What is an Internet Gateway?

An Internet Gateway allows communication between resources in a VPC and the internet, when routing and other requirements are configured correctly.

Navigate to:

```text
VPC → Internet Gateways → Create internet gateway
```

Name:

```text
ExpenseTracker-IGW
```

Create the Internet Gateway.

## Attach Internet Gateway to VPC

Select the newly created Internet Gateway.

Choose:

```text
Actions → Attach to VPC
```

Select:

```text
ExpenseTracker-VPC
```

Click Attach Internet Gateway.

---

# 5. Configure Route Tables

## What is a Route Table?

A route table contains rules that determine where network traffic should be directed.

## 5.1 Public Route Table

Navigate to:

```text
VPC → Route Tables → Create route table
```

Name:

```text
ExpenseTracker-Public-RT
```

VPC:

```text
ExpenseTracker-VPC
```

Create the route table.

## 5.2 Add Internet Route

Select the public route table.

Go to:

```text
Routes → Edit routes → Add route
```

Add:

| Destination | Target |
|---|---|
| 10.0.0.0/16 | local |
| 0.0.0.0/0 | ExpenseTracker-IGW |

The local route is created automatically. Add the internet route manually.

Save changes.

## 5.3 Associate Public Subnet

Navigate to:

```text
Route Tables → ExpenseTracker-Public-RT
→ Subnet associations → Edit subnet associations
```

Select:

```text
ExpenseTracker-Public-Subnet
```

Save the association.

The public subnet is now configured to route internet traffic through the Internet Gateway.

## 5.4 Private Route Table

Create another route table:

```text
ExpenseTracker-Private-RT
```

Associate it with:

```text
ExpenseTracker-Private-Subnet
```

For this project, the private subnet will not have a route to the Internet Gateway.

A NAT Gateway is not required for the current project because we are not deploying resources in the private subnet that need outbound internet access.

---

# 6. Configure Security Groups

## What is a Security Group?

A Security Group acts as a virtual firewall for EC2 instances.

It controls inbound and outbound network traffic.

Navigate to:

```text
AWS Console → EC2 → Security Groups → Create security group
```

Configuration:

| Setting | Value |
|---|---|
| Security Group Name | ExpenseTracker-SG |
| VPC | ExpenseTracker-VPC |

## Inbound Rules

| Type | Port | Source | Purpose |
|---|---|---|---|
| SSH | 22 | My IP | Secure server administration |
| HTTP | 80 | 0.0.0.0/0 | Web application access |

For SSH, use your current public IP address with `/32` whenever possible.

Example:

```text
203.0.113.10/32
```

The example address is illustrative only. Use your actual public IP.

Do not leave SSH open to `0.0.0.0/0` in a production environment.

## Outbound Rules

The default outbound rule allows all outbound traffic.

For the initial deployment, the default outbound rule can be retained.

---

# 7. Launch an Amazon EC2 Instance

## What is EC2?

Amazon EC2 (Elastic Compute Cloud) provides virtual servers in AWS.

We will use EC2 to host the Django Expense Tracker application.

Navigate to:

```text
AWS Console → EC2 → Instances → Launch instances
```

## 7.1 EC2 Configuration

| Setting | Value |
|---|---|
| Name | ExpenseTracker-EC2 |
| AMI | Amazon Linux 2023 |
| Instance Type | Free-tier eligible type if available |
| Key Pair | Create or select an existing key pair |
| VPC | ExpenseTracker-VPC |
| Subnet | ExpenseTracker-Public-Subnet |
| Auto-assign Public IP | Enable |
| Security Group | ExpenseTracker-SG |

Choose the appropriate instance type based on availability, account eligibility and current AWS pricing.

## 7.2 Attach IAM Role

Under Advanced details:

```text
IAM instance profile → ExpenseTracker-EC2-S3-Role
```

If the role is not available during launch, launch the instance and attach it later through:

```text
EC2 → Instances → Select instance
→ Actions → Security → Modify IAM role
```

Select:

```text
ExpenseTracker-EC2-S3-Role
```

Attach the role.

## 7.3 Launch Instance

Review all configurations and click:

```text
Launch instance
```

Wait until:

```text
Instance state: Running
Status checks: 2/2 checks passed
```

---

# 8. Connect to EC2 Using SSH

## What is SSH?

SSH (Secure Shell) is a protocol used to securely connect to remote Linux servers.

## 8.1 Download Key Pair

Download the `.pem` key file during EC2 launch.

Keep the key secure.

Never upload your private key to GitHub.

## 8.2 Connect from Windows PowerShell

Open PowerShell and navigate to the directory containing your key.

Example:

```powershell
cd $HOME\Downloads
```

Check your key file:

```powershell
dir *.pem
```

Connect:

```powershell
ssh -i "your-key.pem" ec2-user@YOUR-EC2-PUBLIC-IP
```

Replace:

- `your-key.pem` with your actual key filename
- `YOUR-EC2-PUBLIC-IP` with the EC2 public IP address

Example:

```powershell
ssh -i "ExpenseTracker.pem" ec2-user@54.123.45.67
```

The IP above is only an example.

## 8.3 Troubleshooting SSH

Test TCP port 22 from Windows:

```powershell
Test-NetConnection YOUR-EC2-PUBLIC-IP -Port 22
```

Expected:

```text
TcpTestSucceeded : True
```

If it returns `False`, check:

- EC2 instance is running
- Status checks are 2/2
- Public IPv4 address is correct
- Security Group permits SSH from your IP
- EC2 is in the public subnet
- Public route table contains `0.0.0.0/0 → Internet Gateway`
- Internet Gateway is attached to the VPC
- Network ACL permits inbound SSH and outbound response traffic
- Your network is not blocking outbound port 22

If your Wi-Fi blocks SSH, test from another network such as a mobile hotspot.

---

# 9. Prepare the EC2 Server

After connecting successfully using SSH, update the server.

```bash
sudo dnf update -y
```

Install required packages:

```bash
sudo dnf install python3 python3-pip git nginx -y
```

Check versions:

```bash
python3 --version
```

```bash
git --version
```

```bash
nginx -v
```

Enable Nginx:

```bash
sudo systemctl enable nginx
```

Start Nginx:

```bash
sudo systemctl start nginx
```

Check its status:

```bash
sudo systemctl status nginx
```

---

# 10. Clone the Django Project from GitHub

Navigate to the home directory:

```bash
cd /home/ec2-user
```

Clone the repository:

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPOSITORY.git
```

Navigate into the project directory:

```bash
cd YOUR-REPOSITORY
```

Check project files:

```bash
ls -la
```

Ensure that the project contains:

```text
manage.py
```

and the Django project files.

---

# 11. Configure Python Virtual Environment

A virtual environment isolates the Python dependencies required by the application.

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file does not exist in the repository, create one locally using:

```bash
pip freeze > requirements.txt
```

Commit and push the file to GitHub before deployment.

---

# 12. Configure Django for AWS

Before deploying, update Django settings.

## 12.1 ALLOWED_HOSTS

Open your Django settings file:

```bash
nano YOUR_PROJECT/settings.py
```

Update `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = [
    "YOUR-EC2-PUBLIC-IP",
    "localhost",
    "127.0.0.1",
]
```

If you later use a domain name, add it to the list.

## 12.2 DEBUG

For deployment:

```python
DEBUG = False
```

Do not run a production server with `DEBUG = True`.

## 12.3 SECRET_KEY

Do not expose the Django secret key in a public repository.

Use an environment variable for production configuration. For example, load the key from an environment variable rather than hardcoding it.

## 12.4 Static Files

Ensure Django has the static files configuration.

Example:

```python
STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
```

Collect static files during deployment:

```bash
python manage.py collectstatic
```

If Django asks for confirmation, type:

```text
yes
```

---

# 13. Run Database Migrations

Apply database migrations:

```bash
python manage.py migrate
```

This creates or updates the database tables required by the Django application.

If the application uses SQLite, the database file will be created in the configured location.

Create an administrator account if required:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email and password.

---

# 14. Test Django on EC2

Before configuring Gunicorn and Nginx, test the Django application directly.

Run:

```bash
python manage.py runserver 0.0.0.0:8000
```

Open your browser:

```text
http://YOUR-EC2-PUBLIC-IP:8000
```

For this temporary test, port 8000 must be allowed in the Security Group.

If you add a port 8000 rule for testing, restrict the source to your IP address and remove the rule after testing.

Stop the development server:

```text
CTRL + C
```

Django's development server should not be used as the permanent production server.

---

# 15. Configure Gunicorn

## What is Gunicorn?

Gunicorn (Green Unicorn) is a Python WSGI application server used to run Django applications in production.

It receives application requests and executes the Django application.

Install Gunicorn inside the virtual environment:

```bash
pip install gunicorn
```

If Gunicorn is required for deployment, add it to `requirements.txt` and commit the update.

## Test Gunicorn

From the directory containing `manage.py`:

```bash
gunicorn YOUR_PROJECT.wsgi:application --bind 127.0.0.1:8000
```

Replace `YOUR_PROJECT` with the actual Django project package name.

Test from the EC2 server:

```bash
curl http://127.0.0.1:8000
```

Stop Gunicorn using:

```text
CTRL + C
```

---

# 16. Configure Gunicorn as a Systemd Service

A systemd service allows Gunicorn to run in the background and start automatically after the server reboots.

Create a service file:

```bash
sudo nano /etc/systemd/system/expense-tracker.service
```

Example configuration:

```ini
[Unit]
Description=Gunicorn service for Expense Tracker Django application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/YOUR-REPOSITORY
ExecStart=/home/ec2-user/YOUR-REPOSITORY/venv/bin/gunicorn YOUR_PROJECT.wsgi:application --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Replace:

- `YOUR-REPOSITORY` with your actual project directory
- `YOUR_PROJECT` with your Django project package

Save the file.

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable the service:

```bash
sudo systemctl enable expense-tracker
```

Start the service:

```bash
sudo systemctl start expense-tracker
```

Check status:

```bash
sudo systemctl status expense-tracker
```

Restart the service whenever required:

```bash
sudo systemctl restart expense-tracker
```

View service logs:

```bash
sudo journalctl -u expense-tracker -f
```

---

# 17. Configure Nginx

## What is Nginx?

Nginx is a web server that can act as a reverse proxy.

In this project:

- Nginx receives HTTP requests from users.
- Nginx serves static files.
- Nginx forwards application requests to Gunicorn.
- Gunicorn executes the Django application.

Architecture:

```text
Browser
   |
   | HTTP :80
   v
 NGINX
   |
   | Proxy
   v
 GUNICORN :8000
   |
   v
 DJANGO APPLICATION
```

## 17.1 Create Nginx Configuration

Create a configuration file:

```bash
sudo nano /etc/nginx/conf.d/expense-tracker.conf
```

Add:

```nginx
server {
    listen 80;
    server_name YOUR-EC2-PUBLIC-IP;

    location /static/ {
        alias /home/ec2-user/YOUR-REPOSITORY/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Replace:

- `YOUR-EC2-PUBLIC-IP`
- `YOUR-REPOSITORY`

with your actual IP and project directory.

## 17.2 Validate Nginx Configuration

```bash
sudo nginx -t
```

Expected:

```text
syntax is ok
test is successful
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

Check status:

```bash
sudo systemctl status nginx
```

---

# 18. Access the Deployed Application

Open a browser:

```text
http://YOUR-EC2-PUBLIC-IP
```

The Django Expense Tracker application should be accessible through Nginx.

The user request flow is:

```text
User
 |
 v
Public IP Address
 |
 v
Nginx :80
 |
 v
Gunicorn :8000 (localhost)
 |
 v
Django
 |
 v
SQLite Database
```

Port 8000 does not need to be exposed publicly when Nginx and Gunicorn are configured correctly.

---

# 19. Create Amazon S3 Backup Bucket

## What is Amazon S3?

Amazon Simple Storage Service (S3) is an object storage service used to store files, backups, logs and other data.

In this project, S3 will be used to store database backups.

Navigate to:

```text
AWS Console → S3 → Create bucket
```

Bucket name:

```text
expense-tracker-anjal-backup
```

S3 bucket names must be globally unique. If the name is unavailable, choose a different unique name and update the IAM policy accordingly.

Recommended settings:

- Block all public access: Enabled
- Bucket versioning: Optional
- Encryption: Enabled (default server-side encryption)
- Public access: Not required

Create the bucket.

---

# 20. Verify EC2 IAM Role Access to S3

Ensure the EC2 instance has this role attached:

```text
ExpenseTracker-EC2-S3-Role
```

Connect to EC2 and check the role credentials are available:

```bash
aws sts get-caller-identity
```

If AWS CLI is not installed:

```bash
sudo dnf install awscli -y
```

Run:

```bash
aws sts get-caller-identity
```

The returned identity should indicate that the EC2 instance is using the attached IAM role.

Do not configure permanent AWS access keys on the EC2 instance.

---

# 21. Create Database Backup and Upload to S3

For a SQLite-based Django application, the database file can be backed up by copying it to a backup directory.

Create a backup directory:

```bash
mkdir -p ~/expense-tracker-backups
```

Copy the database:

```bash
cp /home/ec2-user/YOUR-REPOSITORY/db.sqlite3 \
~/expense-tracker-backups/expense-tracker-backup.sqlite3
```

Upload the backup to S3:

```bash
aws s3 cp ~/expense-tracker-backups/expense-tracker-backup.sqlite3 \
s3://expense-tracker-anjal-backup/backups/expense-tracker-backup.sqlite3
```

List the bucket:

```bash
aws s3 ls s3://expense-tracker-anjal-backup/
```

Download the backup for testing:

```bash
aws s3 cp \
s3://expense-tracker-anjal-backup/backups/expense-tracker-backup.sqlite3 \
~/expense-tracker-backups/restored-database.sqlite3
```

This verifies that the EC2 IAM role can upload and download objects.

Note: For a live SQLite database, copying the file while writes are occurring may not produce a consistent backup. Use a proper SQLite backup method or briefly stop the application before copying, then restart it. For a production application, consider migrating to Amazon RDS.

---

# 22. Configure Amazon CloudWatch Monitoring

## What is CloudWatch?

Amazon CloudWatch is a monitoring and observability service used to collect metrics, logs and alarms from AWS resources.

EC2 provides basic monitoring metrics such as:

- CPU Utilization
- Network In
- Network Out
- Status Checks

Navigate to:

```text
AWS Console → CloudWatch → Metrics → EC2
```

Select the instance metrics.

## Create a CPU Alarm

Navigate to:

```text
CloudWatch → Alarms → Create alarm
```

Select the EC2 CPU utilization metric.

Example configuration:

| Setting | Value |
|---|---|
| Metric | CPU Utilization |
| Threshold | Greater than 80% |
| Evaluation period | 5 minutes |
| Alarm name | ExpenseTracker-High-CPU |

Configure an SNS notification if email alerts are required.

The threshold is an example and can be adjusted depending on the instance type and workload.

## Optional: CloudWatch Logs

CloudWatch Logs can be used to collect:

- Django application logs
- Gunicorn logs
- Nginx logs
- Linux system logs

A CloudWatch Agent can be installed and configured to send system and application logs to CloudWatch Logs.

---

# 23. Deployment Verification Checklist

| Task | Status |
|---|---|
| Django Expense Tracker developed | Completed |
| GitHub repository created | Completed / Verify |
| Custom IAM S3 policy created | Completed |
| EC2 IAM role created | Completed |
| IAM policy attached to role | Verify |
| VPC created | Verify |
| Public subnet created | Verify |
| Private subnet created | Verify |
| Internet Gateway created and attached | Verify |
| Route tables configured | Verify |
| Security Group configured | Verify |
| EC2 instance launched | In progress |
| SSH connection established | In progress |
| Django application deployed | Pending |
| Gunicorn configured | Pending |
| Nginx configured | Pending |
| S3 backup tested | Pending |
| CloudWatch monitoring configured | Pending |

---

# 24. Troubleshooting

## SSH Connection Timeout

Error:

```text
Connection timed out
```

Check:

- Correct public IP address
- EC2 instance running
- EC2 status checks passed
- Security Group inbound SSH rule
- Public subnet route table
- Internet Gateway attachment
- Network ACL
- Local network restrictions

Test:

```powershell
Test-NetConnection YOUR-EC2-PUBLIC-IP -Port 22
```

## Django 400 Bad Request

Possible cause:

```text
Invalid HTTP_HOST header
```

Fix:

Update Django `ALLOWED_HOSTS` with your EC2 public IP or domain name.

## Nginx 502 Bad Gateway

Possible causes:

- Gunicorn is not running
- Incorrect Gunicorn service configuration
- Wrong application package name
- Incorrect proxy configuration

Check:

```bash
sudo systemctl status expense-tracker
```

```bash
sudo journalctl -u expense-tracker -n 50
```

## Static Files Not Loading

Run:

```bash
python manage.py collectstatic
```

Check the Nginx static file directory and configuration:

```bash
sudo nginx -t
```

## S3 Access Denied

Check:

- IAM role attached to EC2
- Custom IAM policy attached to the role
- Bucket name matches policy resources
- Correct bucket ARN and object ARN
- AWS CLI is using the EC2 role
- Bucket policy does not deny access

---

# 25. Security Best Practices

- Restrict SSH access to your IP address.
- Do not expose port 8000 publicly in production.
- Do not store AWS access keys on EC2.
- Use IAM roles for AWS service access.
- Follow the principle of least privilege.
- Keep the S3 bucket private.
- Enable S3 encryption.
- Never commit `.pem` files to GitHub.
- Never upload `.env` files or Django secret keys.
- Set `DEBUG = False` in production.
- Use HTTPS when a domain and TLS configuration are available.
- Regularly update the EC2 operating system.
- Monitor EC2 using CloudWatch.
- Delete unused AWS resources to avoid unexpected charges.

---

# 26. GitHub Repository Setup

Recommended repository structure:

```text
Expense-Tracker/
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── core/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── YOUR_PROJECT/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── templates/
```

Example `.gitignore`:

```gitignore
venv/
.env
*.pem
__pycache__/
*.pyc
db.sqlite3
staticfiles/
.vscode/
.idea/
```

Create requirements:

```bash
pip freeze > requirements.txt
```

Push project changes to GitHub:

```bash
git add .
git commit -m "Document AWS deployment and project setup"
git push origin main
```

---

# 27. Future Improvements

- Configure HTTPS using SSL/TLS
- Configure a custom domain name
- Migrate SQLite to Amazon RDS
- Automate S3 database backups
- Create scheduled backup jobs
- Configure CloudWatch Logs
- Configure CloudWatch alarms and SNS alerts
- Implement CI/CD using Jenkins or GitHub Actions
- Dockerize the Django application
- Implement a production deployment architecture

---

# 28. Learning Outcomes

This project helped me gain practical experience in:

- Django application development
- Linux server administration
- AWS IAM policies and roles
- EC2 instance management
- VPC networking
- Public and private subnets
- Internet Gateway
- Route tables
- Security Groups
- SSH connectivity
- Gunicorn application server
- Nginx reverse proxy
- S3 object storage
- IAM role-based AWS access
- CloudWatch monitoring
- Git and GitHub
- Application deployment troubleshooting

---

# 👨‍💻 Author

**Anjal K**

Computer Science Engineering Graduate | Aspiring DevOps Engineer

GitHub: [anjalk591-in](https://github.com/anjalk591-in)

---

## ⭐ Project

Django Expense Tracker – AWS Cloud Deployment

This project is part of my practical learning journey in AWS, Cloud Computing and DevOps.

