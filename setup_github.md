# GitHub Setup for Background Agents

## Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `ThreadsBot`
3. Make it **Public** (required for background agents)
4. Don't initialize with README (you already have files)
5. Click "Create repository"

## Step 2: Push Your Code
After creating the repository, run:
```bash
git push -u origin main
```

## Step 3: Enable Background Agents in Cursor
1. Open Cursor Settings (Ctrl/Cmd + ,)
2. Go to **General** → **Privacy**
3. **Turn OFF Privacy Mode** (critical for background agents)
4. Go to **Features** → **Beta Features**
5. Enable **Background Agents (Beta)**
6. Connect GitHub with read-write access
7. Grant access to the `lucla/ThreadsBot` repository

## Step 4: Verify Setup
Your repository should be accessible at:
https://github.com/lucla/ThreadsBot

## Current Status
✅ Git repository initialized
✅ Remote URL configured: https://github.com/lucla/ThreadsBot.git
⏳ Waiting for GitHub repository creation
⏳ Waiting for initial push
⏳ Waiting for background agents setup in Cursor

## Troubleshooting
If you get "repository not found" error:
- Make sure you created the repository on GitHub
- Ensure the repository name is exactly "ThreadsBot"
- Verify you're logged into the correct GitHub account (lucla) 