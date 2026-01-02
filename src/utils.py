from typing import Any, Dict
from src.models import GithubPullRequestState, CodeIssue

def confidence_gate(state: GithubPullRequestState) -> Dict[str, Any]:
    review = state.code_review_result
    score = 0.0

    # 1. Issue count
    count = len(review.issues)
    score += 0.3 if 0 < count <= 5 else -0.2

    # 2. Severity balance
    high_ratio = sum(
        i.severity in ("high", "critical")
        for i in review.issues
    ) / max(1, count)

    score += 0.2 if high_ratio < 0.7 else -0.3

    # 3. Grounding  
    grounded = all(
        i.location.file_path in state.diff
        for i in review.issues
    )
    score += 0.3 if grounded else -0.4

    # 4. Reasoning depth
    avg_len = sum(
        len(i.reasoning) for i in review.issues
    ) / max(1, count)

    score += 0.2 if avg_len > 120 else -0.1

    # Clamp
    score = max(0.0, min(score, 1.0))

    print(f"Confidence score: {score}")

    return {
        "confidence": score,
        "should_post": score >= 0.7,
    }

def format_issue_comment(issue: CodeIssue) -> str:
    severity_emoji = {
        "low": "ℹ️",
        "medium": "⚠️",
        "high": "🔴",
        "critical": "🚨"
    }
    
    category_badge = {
        "bug": "🐛 Bug",
        "security": "🔒 Security",
        "performance": "⚡ Performance",
        "style": "💅 Style",
        "maintainability": "🔧 Maintainability"
    }
    
    location_parts = [f"`{issue.location.file_path}`"]
    if issue.location.start_line:
        if issue.location.end_line and issue.location.end_line != issue.location.start_line:
            location_parts.append(f"lines {issue.location.start_line}-{issue.location.end_line}")
        else:
            location_parts.append(f"line {issue.location.start_line}")
    location_str = " • ".join(location_parts)
    
    comment_parts = [
        f"## {severity_emoji.get(issue.severity.value, '⚠️')} {issue.severity.value.upper()} • {category_badge.get(issue.category.value, issue.category.value.title())}",
        "",
        f"**Location:** {location_str}",
        "",
        f"**Issue:** {issue.description}",
        "",
        f"**Reasoning:** {issue.reasoning}",
    ]
    
    return "\n".join(comment_parts)
