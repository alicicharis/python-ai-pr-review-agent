from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.github import GithubService
from src.models import CodeReviewResult, GithubPullRequestState
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from src.prompts import Prompts
from src.utils import confidence_gate, format_issue_comment

load_dotenv()

class Workflow:
    def __init__(self):
        self.github = GithubService()
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0)
        self.prompts = Prompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(GithubPullRequestState)

        graph.add_node('fetch_pull_request', self._fetch_pull_request_step)
        graph.add_node('review_pull_request', self._review_pull_request_step)
        graph.add_node('check_should_post', self._check_should_post_step)
        graph.add_node('post_issue_comment', self._post_issue_comment)

        graph.set_entry_point('fetch_pull_request')

        graph.add_edge('fetch_pull_request', 'review_pull_request')
        graph.add_edge('review_pull_request', 'check_should_post')

        graph.add_conditional_edges(
            "check_should_post",
            lambda state: "post" if state.should_post else "stop",
            {
                "post": "post_issue_comment",
                "stop": END,
            },
        )

        graph.add_edge('post_issue_comment', END)

        return graph.compile()

    def _fetch_pull_request_step(self, state: GithubPullRequestState) -> Dict[str, Any]:
        pull_request_diff = self.github.get_pull_request_diff(state.owner, state.repo, state.pull_number)
        pull_request_files = self.github.get_pull_request_files(state.owner, state.repo, state.pull_number)

        files_changed = [file["filename"] for file in pull_request_files]

        return {
            "diff": pull_request_diff,
            "files_changed": files_changed,
        }

    def _review_pull_request_step(self, state: GithubPullRequestState) -> Dict[str, Any]:
        if not state.diff or not state.files_changed:
            print("Diff and files changed are required")
            return state

        structured_llm = self.llm.with_structured_output(CodeReviewResult)
        messages = [
            SystemMessage(content=self.prompts.REVIEW_PULL_REQUEST_PROMPT),
            HumanMessage(content=f"""
                Diff: {state.diff}
                Files changed: {state.files_changed}
            """),
        ]

        try:
            response = structured_llm.invoke(messages)
            
            return {
                "code_review_result": response
            }
        except Exception as e:
            print(f"Error reviewing pull request: {e}")
            return {"code_review_result": None}

    def _post_issue_comment(self, state: GithubPullRequestState) -> Dict[str, Any]:
        if not state.code_review_result:
            return state

        for issue in state.code_review_result.issues:
            formatted_comment = format_issue_comment(issue)
            self.github.create_issue_comment(state.owner, state.repo, state.pull_number, formatted_comment)
        
        return state

    def _check_should_post_step(self, state: GithubPullRequestState) -> Dict[str, Any]:
        return confidence_gate(state)


    def run(self):
        initial_state = GithubPullRequestState(
            owner="alicicharis",
            repo="notes-mcp-server",
            pull_number=1,
            diff="",
            files_changed=[],
            findings=[],
            security_issues=[],
            suggested_patches=[],
            confidence=0.0,
            should_post=False,
            code_review_result=None,
            improvements=[]
        )
        final_state = self.workflow.invoke(initial_state)
        return GithubPullRequestState(**final_state)
        
