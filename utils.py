import os
import re
from typing import List
from colorama import Fore


def print_color(text: str, color: str, end="\n"):
    print(color + text + Fore.RESET, end=end)


def print_elem(title: str, color: str, text: str = "", end="\n"):
    print_color(title + (":" if text else ""), color, end=" " if text else end)
    if text:
        print(text, end=end)


def print_err(title: str, text: str = "", end="\n"):
    print_elem(title, Fore.RED, text, end=end)


def print_warn(title: str, text: str = "", end="\n"):
    print_elem(title, Fore.YELLOW, text, end=end)


def print_info(title: str, text: str = "", end="\n"):
    print_elem(title, Fore.CYAN, text, end=end)


def print_success(title: str, text: str = "", end="\n"):
    print_elem(title, Fore.GREEN, text, end=end)


def load_file(path: str):
    with open(path, "r") as f:
        lines = f.read().splitlines()

        # Remove commented lines (starting with #), , and empty lines
        lines = [
            line.strip() for line in lines if not line.startswith("#") and line != ""
        ]
    return lines


def check_file(filename: str, check_files: List[str], ignore_files: List[str]) -> bool:
    """Check if filename matches any of the files to check for

    Args:
        filename (str): Filename to check
        check_files (List[str]): List of files to check for
        ignore_files (List[str]): List of files to ignore

    Returns:
        bool: True if filename matches any of the files to check for, False otherwise
    """
    filename = filename.split(os.sep)[-1]
    for check_file_pattern in check_files:
        pattern = re.escape(check_file_pattern).replace(r"\*", ".*")

        if re.match(pattern, filename):
            for ignore_file_pattern in ignore_files:
                pattern = re.escape(ignore_file_pattern).replace(r"\*", ".*")
                if re.match(pattern, filename):
                    return False

            return True


def write_info(base_path: str, content: str, compromised_filename: str):
    """Write the content of a compromised file to a new file in the base path to be analyzed

    Args:
        base_path (str): Base path to write
        content (str): Content of the compromised file
        compromised_filename (str): Name of the compromised file
    """
    filename = f"file_{len(os.listdir(base_path)) + 1}.txt"

    content = f"----- {compromised_filename} -----\n\n{content}"

    with open(os.path.join(base_path, filename), "w") as f:
        f.write(content)
