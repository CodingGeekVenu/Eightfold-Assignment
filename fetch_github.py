import requests
import json

# Replace with your GitHub username, or use a famous one for testing
USERNAME = "octocat" 
URL = f"https://api.github.com/users/{USERNAME}"

response = requests.get(URL)

if response.status_code == 200:
    with open("github_input.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    print(f"[+] Successfully saved {USERNAME}'s data to github_input.json")
else:
    print(f"[!] Failed to fetch data: {response.status_code}")