import requests, json
url = 'http://127.0.0.1:5000/api/login'
payload = {'email': '250893131044.ce24@sltiet.edu.in', 'password': 'sltiet@123'}
headers = {'Content-Type': 'application/json'}
resp = requests.post(url, data=json.dumps(payload), headers=headers)
print('Status:', resp.status_code)
print('Response:', resp.text)
