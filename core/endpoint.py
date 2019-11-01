import os
import requests


class Endpoint():
        def __init__(self):
            self.api=None
            f=open("config.cfg", "r")
            if f:
                for i in f.readlines():
                    if "API_BASE" in i:
                        api=i.split('=')[1]
                        if len(api) > 1:
                            self.api=api.strip()
                print ("Configured API URL %s" % (self.api))
                f.close()

        def post(self,data,endpoint):
            if self.api == None:
                return
            r = requests.post(url=self.api+endpoint, data=data) 
            print(r.text)

        def patch(self,data,endpoint):
            if self.api == None:
                return
            r = requests.patch(url=self.api+endpoint, data=data) 
            print(r.text)        

        def get(self,data,endpoint):
            if self.api == None:
                return "{}"
            r = requests.get(url=self.api+endpoint) 
            return r.text         
