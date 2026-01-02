from dotenv import load_dotenv
from src.workflow import Workflow

load_dotenv()

def main():
    workflow = Workflow()
    result = workflow.run()
    print(f"Result: {result}")

if __name__ == "__main__":
    main()