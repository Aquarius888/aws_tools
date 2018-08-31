#!/usr/bin/env python3

import requests
import settings

user = str(settings.user)
password = str(settings.password)

url = 'https://ads.lab.nordigy.ru/api/v2/dep-request/'
id_req = '123667'

req = requests.get(url + id_req, auth=(user, password))

print(req)
