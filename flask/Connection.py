import requests
import hashlib
import json
from requests.auth import HTTPDigestAuth
import curlify
replytoken = 'a76654d8e3550e9a2d67a0eeb6c67b220e5885eddd3fde135806e601'
body = {'ReplyToken': '',
        'Text':['頭','けが'],
        'Form':{'UserId':'abcd','Sex':'male','BirthYear':'2021',"PostalCode":"123456"},
        'MessageId':'abcd',
        'Inverted':False,
        }
#print(json.dumps(body).encode('utf-8').hex())
sig = hashlib.sha256(json.dumps(body).encode('utf-8').hex().encode()).hexdigest()
bearer = hashlib.sha256('NAIST'.encode()).hexdigest()
#print(bearer)
#Base = 'http://127.0.0.1:5000/'
Base = 'http://aoi.naist.jp/patient/'
response = requests.post(Base+'API',
                         json=body,

                         headers={'Authorization': 'Bearer '+bearer,'content-type':'application/json','X-AIHospital-Signature':sig})
print(curlify.to_curl(response.request))
print(response,response.json())


