#!/bin/bash

# Check if commit message is provided as an argument
if [ -z "$1" ]; then
  echo "Please provide a commit message."
  exit 1
fi

# Initialize Git repository if not already initialized
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

# Add all changes to the staging area
git add -A

# Commit changes with the provided commit message
git commit -m "$1"

# Push changes to GitHub
git push origin master

echo "Repository committed and pushed successfully."

