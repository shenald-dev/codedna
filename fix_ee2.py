with open("codedna/analyzers/evolution_engine.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD\n        import re\n\n=======\n>>>>>>> origin/master\n", "        import re\n")

with open("codedna/analyzers/evolution_engine.py", "w") as f:
    f.write(content)
