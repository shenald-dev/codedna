with open("codedna/analyzers/code_smell_detector.py", "r") as f:
    content = f.read()

content = content.replace(
    "<<<<<<< HEAD\nPY_METHOD_PATTERN = re.compile(r\"^\\s*def\\s+\\w+\", re.MULTILINE)\nJS_METHOD_PATTERN = re.compile(r\"(?:function\\s+\\w+|=>\\s*\\{|\\b[a-zA-Z_]\\w*\\s*\\([^)]*\\)\\s*\\{)\")\nJAVA_METHOD_PATTERN = re.compile(r\"(?:public|private|protected)\\s+\\w+\\s+\\w+\\s*\\(\")\nPY_FUNC_START_PATTERN = re.compile(r\"^(\\s*)def\\s+(\\w+)\", re.MULTILINE)\n=======\nPY_METHOD_PATTERN = re.compile(r\"^[ \\t]*def\\s+\\w+\")\nJS_METHOD_PATTERN = re.compile(r\"(function\\s+\\w+|=>\\s*\\{|\\b[a-zA-Z_]\\w*\\s*\\([^)]*\\)\\s*\\{)\")\nJAVA_METHOD_PATTERN = re.compile(r\"(public|private|protected)\\s+\\w+\\s+\\w+\\s*\\(\")\nPY_FUNC_START_PATTERN = re.compile(r\"^([ \\t]*)def\\s+(\\w+)\")\n>>>>>>> origin/master",
    "PY_METHOD_PATTERN = re.compile(r\"^[ \\t]*def\\s+\\w+\")\nJS_METHOD_PATTERN = re.compile(r\"(?:function\\s+\\w+|=>\\s*\\{|\\b[a-zA-Z_]\\w*\\s*\\([^)]*\\)\\s*\\{)\")\nJAVA_METHOD_PATTERN = re.compile(r\"(?:public|private|protected)\\s+\\w+\\s+\\w+\\s*\\(\")\nPY_FUNC_START_PATTERN = re.compile(r\"^([ \\t]*)def\\s+(\\w+)\")"
)

with open("codedna/analyzers/code_smell_detector.py", "w") as f:
    f.write(content)
