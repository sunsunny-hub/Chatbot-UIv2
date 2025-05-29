import os
import requests
import subprocess

def get_pr_diff():
    # Obtain the diff of the last commit for simplicity.
    result = subprocess.run(["git", "diff", "HEAD~1", "HEAD"], capture_output=True, text=True)
    return result.stdout
def call_azure_openai(prompt_text):
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]
    
    url = f"{endpoint}/openai/deployments/gpt-4.1/completions?api-version=2025-04-14"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = {
        "prompt": prompt_text,
        "max_tokens": 250,
        "temperature": 0.5,
        "stop": None
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    else:
        print("Error calling Azure OpenAI:", response.text)
        return None
def post_github_comment(comment_text):
    pr_number = os.environ.get("GITHUB_REF").split('/')[-1]
    repo = os.environ.get("GITHUB_REPOSITORY")
    github_token = os.environ.get("GITHUB_TOKEN")
    
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json"
    }
    
    data = {"body": comment_text}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print("Comment posted successfully!")
    else:
        print("Error posting comment:", response.text)
def main():
    diff = get_pr_diff()
    if not diff:
        print("No changes found.")
        return
    # Professional prompt for detailed PR analysis.
    prompt_text = (
        "You are a code review and software engineering expert. Analyze the following pull request changes and provide a detailed report that includes:\n"
        "- Main changes (new features, bug fixes, refactorings)\n"
        "- Points of attention and suggestions for improvement\n"
        "- Potential impact on functionality and code quality\n\n"
        "Here is the diff:\n\n" + diff
    )
    
    response_text = call_azure_openai(prompt_text)
    if response_text:
        try:
            main_summary, suggestions = response_text.split("Suggestions:", 1)
        except ValueError:
            main_summary = response_text
            suggestions = "No additional suggestions generated."
        
        comment_text = (
            "### Automated PR Summary\n\n"
            "**Main Changes:**\n" + main_summary.strip() + "\n\n"
            "**Improvement Suggestions:**\n" + suggestions.strip()
        )
        post_github_comment(comment_text)
    else:
        print("Could not generate a summary.")
if __name__ == "__main__":
    main()
