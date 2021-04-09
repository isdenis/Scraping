import requests
import json

username = 'isdenis'
token = 'xxxxxxxxxxxxx'
main_link = f'https://api.github.com/users/{username}/repos'
response = requests.get(main_link, auth=(username, token))
j_data = response.json()

repository = {}
n = 1
for repo in j_data:
    print(repo['name'])
    repository[f'repository {n}'] = repo['name']
    n += 1
print(repository)

with open('response.json', 'w', encoding='utf-8') as file:
    json.dump(repository, file, indent=2, ensure_ascii=False)
