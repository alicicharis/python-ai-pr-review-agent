from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from enum import Enum

class CodeLocation(BaseModel):
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None

class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"


class CodeIssue(BaseModel):
    id: str = Field(..., description="Stable identifier for this issue")
    category: IssueCategory
    severity: IssueSeverity
    description: str
    location: CodeLocation
    reasoning: str

class CodeReviewResult(BaseModel):
    summary: str
    issues: List[CodeIssue]
    overall_risk: Literal["low", "medium", "high", "critical"]

class GithubPullRequestState(BaseModel):
    owner: str
    repo: str
    pull_number: int

    diff: str
    files_changed: List[str]

    findings: List[str]
    security_issues: List[str]

    suggested_patches: List[str]

    confidence: float
    should_post: bool

    code_review_result: Optional[CodeReviewResult]

    improvements: List[str]