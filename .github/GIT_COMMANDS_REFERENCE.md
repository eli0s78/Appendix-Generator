# 📚 Git Commands Quick Reference

Essential Git commands for your development workflow.

## 🔄 Daily Workflow

### Check Status
```bash
git status                    # See what files changed
```

### Stage Changes
```bash
git add .                     # Add all changes
git add filename.py           # Add specific file
git add utils/                # Add entire folder
```

### Commit Changes
```bash
git commit -m "Your message"  # Commit with message
```

### Push to GitHub
```bash
git push origin main          # Push to main branch
```

### Combined (most common workflow)
```bash
git add .
git commit -m "Add new feature"
git push origin main
```

## 📥 Pulling Changes

### Get Latest from GitHub
```bash
git pull origin main          # Pull and merge
git pull --rebase origin main # Pull and rebase (cleaner history)
```

## 🌿 Branching

### Create and Switch to New Branch
```bash
git checkout -b feature-name  # Create and switch
```

### Switch Between Branches
```bash
git checkout main             # Switch to main
git checkout feature-name     # Switch to feature branch
```

### List All Branches
```bash
git branch                    # Local branches
git branch -a                 # All branches (including remote)
```

### Merge Branch
```bash
git checkout main             # Switch to main
git merge feature-name        # Merge feature into main
```

### Delete Branch
```bash
git branch -d feature-name    # Delete local branch (safe)
git branch -D feature-name    # Force delete local branch
```

## 🔍 Viewing History

### View Commits
```bash
git log                       # Full log
git log --oneline             # Compact log
git log --oneline -10         # Last 10 commits
git log --graph --oneline     # Visual branch graph
```

### View Changes
```bash
git diff                      # Unstaged changes
git diff --staged             # Staged changes
git diff filename.py          # Changes in specific file
```

### View Specific Commit
```bash
git show COMMIT_HASH          # Show commit details
```

## ⏮️ Undoing Changes

### Discard Local Changes (Not Committed)
```bash
git checkout -- filename.py   # Discard changes in file
git checkout -- .             # Discard all changes
```

### Unstage Files
```bash
git reset filename.py         # Unstage specific file
git reset                     # Unstage all files
```

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1       # Undo commit, keep changes staged
git reset HEAD~1              # Undo commit, keep changes unstaged
```

### Undo Last Commit (Discard Changes)
```bash
git reset --hard HEAD~1       # ⚠️ WARNING: Deletes changes!
```

### Revert a Commit (Create New Commit)
```bash
git revert COMMIT_HASH        # Safe way to undo
```

## 🔗 Remote Repository

### View Remote
```bash
git remote -v                 # Show remote URLs
```

### Add Remote
```bash
git remote add origin URL     # Add remote
```

### Change Remote URL
```bash
git remote set-url origin NEW_URL
```

### Remove Remote
```bash
git remote remove origin
```

## 🏷️ Tags

### Create Tag
```bash
git tag v1.0.0                # Create lightweight tag
git tag -a v1.0.0 -m "Version 1.0.0"  # Annotated tag
```

### Push Tags
```bash
git push origin v1.0.0        # Push specific tag
git push origin --tags        # Push all tags
```

### List Tags
```bash
git tag                       # List all tags
```

## 🔧 Configuration

### Set User Info
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### View Configuration
```bash
git config --list             # All settings
git config user.name          # Specific setting
```

## 🆘 Troubleshooting

### Merge Conflicts
```bash
# 1. Open conflicted files and resolve manually
# 2. Mark as resolved:
git add filename.py
# 3. Complete merge:
git commit
```

### Forgot to Add Files to Commit
```bash
git add forgotten-file.py
git commit --amend --no-edit  # Add to last commit
```

### Change Last Commit Message
```bash
git commit --amend -m "New message"
```

### Recover Deleted Commits
```bash
git reflog                    # Find commit hash
git checkout COMMIT_HASH      # Restore
```

### Force Push (Use Carefully!)
```bash
git push --force origin main  # ⚠️ Only if you're sure!
```

## 📋 .gitignore

### Create .gitignore
```bash
# Add to .gitignore file:
*.pyc
__pycache__/
.env
*.log
```

### Remove Tracked File (But Keep Locally)
```bash
git rm --cached filename.py
```

## 🎯 Pro Tips

### Beautiful Git Log
```bash
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
```

### Create Alias for This
```bash
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
# Now use: git lg
```

### Interactive Staging
```bash
git add -p                    # Stage parts of files
```

### Stash Changes (Temporary Save)
```bash
git stash                     # Save changes
git stash pop                 # Restore changes
git stash list                # List stashes
git stash clear               # Delete all stashes
```

## 🚀 GitHub-Specific

### Clone Repository
```bash
git clone URL                 # Clone repo
git clone URL folder-name     # Clone to specific folder
```

### Fork Workflow
```bash
# Add upstream (original repo)
git remote add upstream ORIGINAL_REPO_URL

# Get latest from original
git fetch upstream
git merge upstream/main
```

---

## 📖 Learn More

- [Official Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet PDF](https://education.github.com/git-cheat-sheet-education.pdf)

---

**Bookmark this file for quick reference!**
