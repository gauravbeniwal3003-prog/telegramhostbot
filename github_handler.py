import base64
from github import Github
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH

_gh = None
_repo = None

def _get_repo():
    global _gh, _repo
    if _repo is None:
        _gh = Github(GITHUB_TOKEN)
        _repo = _gh.get_repo(GITHUB_REPO)
    return _repo

def upload_files(folder: str, files: list):
    repo = _get_repo()
    links = []
    for f in files:
        path = f"{folder}/{f['name']}"
        content_b64 = base64.b64encode(f["content"]).decode()
        try:
            existing = repo.get_contents(path, ref=GITHUB_BRANCH)
            repo.update_file(path, f"update {path}", content_b64, existing.sha, branch=GITHUB_BRANCH)
        except Exception:
            repo.create_file(path, f"add {path}", content_b64, branch=GITHUB_BRANCH)
        raw = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{path}"
        links.append({"name": f["name"], "url": raw})
    return links

def test_connection():
    try:
        repo = _get_repo()
        return True, f"OK: {repo.full_name}"
    except Exception as e:
        return False, str(e)
