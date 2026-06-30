import requests, json
url = 'http://127.0.0.1:5000/api/login'
payload = {"email": "250893131044.ce24@sltiet.edu.in", "password": "sltiet@123"}
try:
    r = requests.post(url, json=payload, timeout=5)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
# version control python 
# i just develop web portel into python 3.13 using flask now i want to deply and run into  same conneteced network wile is system is the server and other are the clients so how can i do that please give me the step by step guide to run my web portal into same network and access from other system which is connected to same network computers with no spafici version then how can i cofigure it.
#  