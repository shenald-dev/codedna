import re

with open(".jules/bolt.md", "r") as f:
    content = f.read()

content = re.sub(r'<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> origin/master', r'\1', content, flags=re.DOTALL)

with open(".jules/bolt.md", "w") as f:
    f.write(content)
