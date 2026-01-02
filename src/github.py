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
    
    def _get_base_url(self) -> str:
        base_url = os.getenv('GITHUB_API_URL', 'https://api.github.com')
        return base_url.rstrip('/')

    def _get(self, path: str, headers: dict = None, return_text: bool = False):
        request_headers = headers if headers else {}
        url = f"{self._get_base_url()}{path}"
        response = self.session.get(url, headers=request_headers)
        response.raise_for_status()
        return response.text if return_text else response.json()

    def _post(self, path: str, json: dict):
        url = f"{self._get_base_url()}{path}"
        response = self.session.post(url, json=json)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code} Error: {e}\nURL: {url}"
            try:
                error_body = response.json()
                if "message" in error_body:
                    error_msg += f"\nGitHub API message: {error_body['message']}"
                if "errors" in error_body:
                    error_msg += f"\nGitHub API errors: {error_body['errors']}"
            except:
                error_msg += f"\nResponse body: {response.text[:500]}"
            raise requests.exceptions.HTTPError(error_msg, response=response)
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

    def create_issue_comment(self, owner: str, repo: str, pull_number: int, comment: str):
        return self._post(f"/repos/{owner}/{repo}/issues/{pull_number}/comments", json={"body": comment})
