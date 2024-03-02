# Overview

Git is awesome, but have you ever hit `git push` command, and then 'Oh \*\*\*\*, I just pushed `credentials.yaml`'? Well, I have! And I'm sure you have too.

This is a simple script to help you find and revoke sensitive information from your git history.

## How it works

This script will check the git repositories from a given directory, and check for files matching a pattern, for each commit you made, that you might have pushed by mistake. Theses files will be displayed and their content will be written inside the `out` directory so you can inspect them and revoke the necessary credentials.

## Get started

1. Set the patterns you want to search for in the `check_patterns.txt` file. Some are already set, but you can add your own.
2. Set the patterns you want to ignore in the `ignore_patterns.txt` file. Some are already set, but you can add your own. (`.env.example` is a good example of a file that you don't want to check)
3. Install the dependencies with `pip install -r requirements.txt` (preferably in a virtual environment)
4. Run the script

## Usage

```bash
python main.py --root=PATH_TO_YOUR_GIT_REPOSITORIES
```
