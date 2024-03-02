import os

import pathlib
import utils
import argparse
from GitRepo import GitRepo
import shutil


ROOT_DIR = pathlib.Path(__file__).parent.absolute().as_posix()

CHECK_FILES_NAME = "check_patterns.txt"
IGNORE_FILES_NAME = "ignore_patterns.txt"
OUT_DIR = os.path.join(ROOT_DIR, "out")


#################### Load files ####################

# Load files to check patterns for
CHECK_FILES = utils.load_file(os.path.join(ROOT_DIR, CHECK_FILES_NAME))

# Load files to ignore patterns for
IGNORE_FILES = utils.load_file(os.path.join(ROOT_DIR, IGNORE_FILES_NAME))

utils.print_info("Check patterns", str(len(CHECK_FILES)))
utils.print_info("Ignore patterns", str(len(IGNORE_FILES)), end="\n\n")


def main(root_dir: str):
    # Create directory to store output
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)

    os.makedirs(OUT_DIR)

    # Get all git repositories in the root directory
    utils.print_info("Finding Git repositories...", end="\n\n")
    git_repos = GitRepo.find_all(root_dir)

    if git_repos:
        for repo in git_repos:
            utils.print_info("\n\nProcessing Git repository", repo.root_dir)
            out_dir = "_".join(repo.root_dir.split(os.sep)[-2:])

            # Iterate through all branches
            for branch in repo.branches:
                print(f"Branch: {branch}")
                try:
                    repo.switch_branch(branch)
                except Exception as e:
                    utils.print_err("Failed to checkout to branch", str(e))
                    continue

                # Get all commits for the current branch
                commit_hashes = repo.get_commit_hashes()

                # Get all files added by each commit, and check whether they match the patterns
                for commit_hash in commit_hashes:
                    files = repo.get_files_added_by_commit(commit_hash)
                    for file in files:
                        if utils.check_file(file, CHECK_FILES, IGNORE_FILES):
                            utils.print_err("File matched", f"{file} in {commit_hash}")

                            # Create directory for the commit hash
                            commit_dir = os.path.join(
                                OUT_DIR, out_dir, branch, commit_hash
                            )
                            os.makedirs(commit_dir, exist_ok=True)

                            # Write the file content to the commit directory to inspect
                            utils.write_info(
                                commit_dir,
                                repo.get_file_content_by_commit(commit_hash, file),
                                file,
                            )

            repo.switch_back_to_original_branch()
            repo.unclone()  # Remove tmp directory

    else:
        print("No Git repositories found in the specified root directory.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check files against patterns")

    # Root dir to check for files (must be an existing directory).
    parser.add_argument(
        "--root",
        type=str,
        required=True,
        help="Root directory to check. Must be an existing directory.",
    )

    args = parser.parse_args()

    # Expand user so that ~ is recognized
    root_dir = os.path.abspath(os.path.expanduser(args.root))
    utils.print_info(title="Root directory", text=root_dir, end="\n\n")

    if not os.path.exists(root_dir):
        utils.print_err(f"Root directory {root_dir} does not exist")
        exit(1)

    main(root_dir)

    utils.print_success("\nDone!")
    print(
        "Check the out folder to inspect compromised files and revoke access to the necessary resources."
    )
