import requests
import json

version = '5.52'
access_token = 'xxxxxxxxxxxxx'
main_link = f'https://api.vk.com/method/friends.getSuggestions'
params = {'v': '5.52',
          'access_token': access_token}
response = requests.get(main_link, params=params)

if response.ok:
    j_data = response.json()
    with open('maybe_friends.json', 'w', encoding='utf-8') as file:
        json.dump(j_data, file, indent=2, ensure_ascii=False)
else:
    print('Что-то пошло не так :(')
