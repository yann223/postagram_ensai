import subprocess

# Destroy main_server.py
subprocess.run(["cdktf", "destroy", "-a", "pipenv run python3 main_server.py"], cwd="terraform", check=True)

# Destroy main_server.py
subprocess.run(["cdktf", "destroy", "-a", "pipenv run python3 main_serverless.py"], cwd="terraform", check=True)


# Change back bucket name
main_server_file = "terraform/main_server.py"
with open(main_server_file, "r") as file:
    script_content = file.readlines()

for i, line in enumerate(script_content):
    if line.startswith("bucket = "):
        new_bucket_name = "BUCKET_NAME_PLACEHOLDER"
        script_content[i] = f"bucket = \"{new_bucket_name}\"\n"
        break

with open(main_server_file, "r") as file:
    file.writelines(script_content)


# Change back dns name
index_file = "webapp/src/index.js"
with open(index_file, "r") as file:
    script_content = file.readlines()

for i, line in enumerate(script_content):
    if line.startswith("axios.defaults.baseURL = "):
        new_dns_name = "http://LB_DNS_NAME_PLACEHOLDER:8080/"
        script_content[i] = f"bucket = \"{new_dns_name}\"\n"
        break

with open(index_file, "r") as file:
    file.writelines(script_content)