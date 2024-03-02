import os
from typing import List
import git
import utils


class GitRepo:

    CLONING_DIR = "/tmp"

    def __init__(self, root_dir: str):
        self.name = f"gitrepo_{os.path.basename(root_dir)}"
        self.clone_path = os.path.join(GitRepo.CLONING_DIR, self.name)

        while os.path.exists(self.clone_path):
            self.name += "0"
            self.clone_path = os.path.join(GitRepo.CLONING_DIR, self.name)

        self.root_dir = root_dir

        # Clone the repository to avoid modifying the original
        self.clone()

        self.repo = git.Repo(self.clone_path)
        self.repo.remotes.origin.fetch()

        self.original_branch = self.repo.active_branch
        self.current_branch = self.repo.active_branch

        self.branches = [branch.name for branch in git.Repo(root_dir).branches]

    @staticmethod
    def find_all(root_dir: str):
        """Get all git repositories in the root directory

        Args:
            root_dir (str): Root directory to search for git repositories

        Returns:
            List[GitRepo]: List of git repositories found in the root directory
        """
        git_repos: List[GitRepo] = []

        for dirpath, dirnames, _ in os.walk(root_dir):
            if ".git" in dirnames:
                git_repo_path = os.path.join(dirpath, ".git")

                try:
                    repo = GitRepo(os.path.dirname(git_repo_path))
                    git_repos.append(repo)
                except Exception:
                    pass

        return git_repos

    def switch_branch(self, target_branch: str):
        """Switch to a different branch

        Args:
            target_branch (str): Branch to switch to
        """
        self.repo.git.checkout(target_branch)
        self.current_branch = self.repo.active_branch

    def switch_back_to_original_branch(self):
        """Switch back to the original branch"""
        self.repo.git.checkout(self.original_branch)
        self.current_branch = self.original_branch

    def get_commit_hashes(self) -> List[str]:
        """Get all commit hashes for the current branch

        Returns:
            List[str]: List of commit hashes for the current branch
        """
        return [commit.hexsha for commit in self.repo.iter_commits()]

    def get_files_added_by_commit(self, commit_hash: str) -> List[str]:
        """Get all files added by a commit

        Args:
            commit_hash (str): Commit hash to get files added by

        Returns:
            List[str]: List of files added by the commit
        """
        commit = self.repo.commit(commit_hash)
        try:
            return [diff.a_path for diff in commit.diff(commit.hexsha + "^")]
        except Exception:
            return []

    def get_file_content_by_commit(self, commit_hash: str, file_path: str) -> str:
        """Get the content of a file at a specific commit

        Args:
            commit_hash (str): Commit hash to get file content from
            file_path (str): File path to get content from

        Returns:
            str: Content of the file at the specific commit
        """
        commit = self.repo.commit(commit_hash)
        try:
            return commit.tree[file_path].data_stream.read().decode("utf-8")
        except Exception:
            return ""

    def get_url(self) -> str:
        """Get the URL of the remote origin

        Returns:
            str: URL of the remote origin
        """
        # return self.repo.remotes.origin.url
        with open(os.path.join(self.root_dir, ".git", "config"), "r") as f:
            lines = f.read().splitlines()
            for i, line in enumerate(lines):
                if line.strip() == '[remote "origin"]':
                    url = lines[i + 1].split("=")[1].strip()
                    return url

    def clone(self):
        """Clone the repository to avoid modifying the original"""
        url = self.get_url()
        if not url:
            return

        try:
            print(f"Cloning repo... ({url})")
            git.Repo.clone_from(url, self.clone_path)
        except Exception as e:
            utils.print_err("Error cloning repo", str(e))

            try:
                self.unclone()
            except Exception:
                pass

            raise e

    def unclone(self):
        """Remove the cloned repository"""
        os.system(f"rm -rf {self.clone_path}")
