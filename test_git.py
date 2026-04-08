import time
from git import Repo

repo = Repo(".")
start = time.time()
for commit in repo.iter_commits(max_count=100):
    files = commit.stats.files
print("Git stats time:", time.time() - start)
