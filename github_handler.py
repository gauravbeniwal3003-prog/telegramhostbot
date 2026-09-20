import os
import json
import base64
from github import Github
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH

_gh = Github(GITHUB_TOKEN)
_repo = _gh.get_repo(GITHUB_REPO)

def upload_files(folder: str, files: list):
    """
    files = list of dicts: { "name": "main.py", "content": bytes }
    Returns list of raw GitHub URLs.
    """
    links = []
    for f in files:
        path = f"{folder}/{f['name']}"
        content_b64 = base64.b64encode(f["content"]).decode()

        try:
            existing = _repo.get_contents(path, ref=GITHUB_BRANCH)
            _repo.update_file(path, f"update {path}", content_b64, existing.sha, branch=GITHUB_BRANCH)
        except Exception:
            _repo.create_file(path, f"add {path}", content_b64, branch=GITHUB_BRANCH)

        raw = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{path}"
        links.append({"name": f["name"], "url": raw})

    return links
