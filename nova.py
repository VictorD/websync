#!/usr/bin/env python
from novaclient.v1_1 import client
import os

#nova --os-username "student-project-9" --os-tenant-id="b0f27ff1c56b4e18a893157d1cfee705" --os-auth-url="http://130.240.233.106:5000/v2.0" --os-password="jTKmDEO5Xl5H" image-list

nv = client.Client(username="student-project-9",
                   api_key="jTKmDEO5Xl5H",
                   project_id="student-project-9", 
                   auth_url="http://130.240.233.106:5000/v2.0")
                   
print nv.flavors.list()
print nv.servers.list()
 