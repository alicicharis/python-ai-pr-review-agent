import os
from dotenv import load_dotenv
import requests

load_dotenv()

class GithubService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json",
        })

    def _get(self, path: str, headers: dict = None, return_text: bool = False):
        request_headers = headers if headers else {}
        response = self.session.get(f"{os.getenv('GITHUB_API_URL')}{path}", headers=request_headers)
        response.raise_for_status()
        return response.text if return_text else response.json()

    def _post(self, path: str, json: dict):
        response = self.session.post(f"{os.getenv('GITHUB_API_URL')}{path}", json=json)
        response.raise_for_status()
        return response.json()

    def get_pull_request(self, owner: str, repo: str, pull_number: int):
        return self._get(f"/repos/{owner}/{repo}/pulls/{pull_number}")

    def get_pull_request_files(self, owner: str, repo: str, pull_number: int):
        return self._get(f"/repos/{owner}/{repo}/pulls/{pull_number}/files")

    def get_pull_request_diff(self, owner: str, repo: str, pull_number: int):
        return self._get(
            f"/repos/{owner}/{repo}/pulls/{pull_number}",
            headers={"Accept": "application/vnd.github.v3.diff"},
            return_text=True
        )