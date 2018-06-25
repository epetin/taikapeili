from subprocess import call

with open("urls.txt", "r") as f:
    for line in f:
        call(["wget", line.strip()])