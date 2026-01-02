from dotenv import load_dotenv
from src.github import GithubService

load_dotenv()

def main():
    github = GithubService()
    res = github.get_pull_request("alicicharis","notes-mcp-server", 1)

    print(f"Res: {res}")

if __name__ == "__main__":
    main()