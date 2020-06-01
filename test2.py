import subprocess

IP = subprocess.check_output(["hostname", "-I"]).split()[0]
print(str(IP)[2:-1])