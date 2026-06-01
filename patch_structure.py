with open('codedna/analyzers/structure_analyzer.py', 'r') as f:
    content = f.read()
import re
content = re.sub(r'<<<<<<< HEAD.*?file_count_cache = None\n=======.*?file_count = None\n>>>>>>> origin/master', r'            # Cache assumes `items` is not mutated during the current directory\'s loop.\n            file_count_cache = None', content, flags=re.DOTALL)
content = re.sub(r'<<<<<<< HEAD.*?if file_count_cache is None:.*?file_count_cache = sum\(1 for p in items if p\.is_file\(\)\).*?=======.*?if file_count is None:.*?file_count = sum\(1 for p in items if p\.is_file\(\)\).*?>>>>>>> origin/master', r'                            if file_count_cache is None:\n                                file_count_cache = sum(1 for p in items if p.is_file())', content, flags=re.DOTALL)
with open('codedna/analyzers/structure_analyzer.py', 'w') as f:
    f.write(content)
