import subprocess

# Deploy main_serverless.py
subprocess.run(["cdktf", "deploy", "-a", "pipenv run python3 main_serverless.py"], cwd="terraform", check=True)

# Retrieve bucket name from Terraform output
print("Paste here the bucket id from the output")
bucket_name = input()

# Update main_server.py with bucket name
main_server_file = "terraform/main_server.py"
with open(main_server_file, "r") as f:
    content = f.read()
content = content.replace("BUCKET_NAME_PLACEHOLDER", bucket_name)
with open(main_server_file, "w") as f:
    f.write(content)

# Deploy main_server.py
subprocess.run(["cdktf", "deploy", "-a", "pipenv run python3 main_server.py"], cwd="terraform", check=True)

# Retrieve Load Balancer DNS name from Terraform output
print("Paste here the dns name from the output.")
lb_dns_name = input()

# Update index.js with EC2 DNS name
index_js_file = "webapp/src/index.js"
with open(index_js_file, "r") as f:
    content = f.read()
content = content.replace("LB_DNS_NAME_PLACEHOLDER", lb_dns_name)
with open(index_js_file, "w") as f:
    f.write(content)

# Run the webapp
subprocess.run(["npm", "install"], cwd="webapp", check=True)
subprocess.run(["npm", "start"], cwd="webapp", check=True)
