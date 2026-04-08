import os

with open(".jules/warden.md", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith("<<<<<<< HEAD"):
        skip = True
    elif line.startswith("======="):
        skip = False
    elif line.startswith(">>>>>>>"):
        pass
    elif not skip:
        new_lines.append(line)

with open(".jules/warden.md", "w") as f:
    f.writelines(new_lines)

with open("CHANGELOG.md", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith("<<<<<<< HEAD"):
        skip = True
    elif line.startswith("======="):
        skip = False
    elif line.startswith(">>>>>>>"):
        pass
    elif not skip:
        new_lines.append(line)

with open("CHANGELOG.md", "w") as f:
    f.writelines(new_lines)
