#!/bin/bash
sed -i '/<<<<<<< HEAD/d' .jules/bolt.md
sed -i '/=======/d' .jules/bolt.md
sed -i '/>>>>>>> origin\/master/d' .jules/bolt.md
git add .jules/bolt.md
git commit -m "Merge branch 'master' into fix/git-log-format-prefix-8887929926089236422"
