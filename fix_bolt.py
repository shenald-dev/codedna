import sys

with open('.jules/bolt.md', 'r') as f:
    content = f.read()

import re

new_content = re.sub(
    r"<<<<<<< HEAD\n+2026-05-26 — Fix Git log formatting\nLearning: Modern Git requires the tformat: prefix for custom formats to avoid fatal parsing errors and preserve standard terminator behavior.\nAction: Use the tformat: prefix instead of relying on unprefixed --format strings.\n=======\n",
    "",
    content
)

new_content = new_content.replace(">>>>>>> origin/master\n", "")

with open('.jules/bolt.md', 'w') as f:
    f.write(new_content)
