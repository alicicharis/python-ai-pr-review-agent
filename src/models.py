from pydantic import BaseModel
from typing import List

class GithubPullRequest(BaseModel):
    repo: str
    pr_number: int

    diff: str
    files_changed: List[str]

    findings: List[str]
    security_issues: List[str]

    suggested_patches: List[str]

    confidence: float
    should_post: bool
