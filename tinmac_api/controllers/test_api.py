import json
import random
import urllib.request
from cryptography.fernet import Fernet
print('yes')

data = {
'username' : 'admin',
'password' : 'odoo16@2022',
#'update_data' : {'name':'nilesh'},
}

# req = urllib.request.Request(url="http://185.209.229.33:8024/asset/order/order_info/1", data=json.dumps(data).encode(), headers={
#        "Content-Type":"application/json",
#    })
# reply = json.loads(urllib.request.urlopen(req).read().decode('UTF-8'))
# print(reply)



# we will be encrypting the below string.
password = "odoo16@2022"
key = "nsHhkPbOUf1CfDfvqKzyxcri6eIi3FOKxQFu_lpY4xw="
fernet = Fernet(key)
encMessage = fernet.encrypt(password.encode())
data = {
'username' : 'admin',
'password' : encMessage.decode("utf-8"),
#'update_data' : {'name':'nilesh'},
'session' : 'a397070db8094b9baee713d60e0a9f7ca025213045697a5f0e52332ec6653e74',
}
print('fd')
req = urllib.request.Request(url="http://localhost:10017/asset/asset_master_list", data=json.dumps(data).encode(), headers={
       "Content-Type":"application/json",
   })

reply = json.loads(urllib.request.urlopen(req).read().decode('UTF-8'))
print(reply)


