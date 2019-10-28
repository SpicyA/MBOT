import os
import requests


class Endpoint():
        def __init__(self):
            self.ep_1=None
            self.ep_2=None
            f=open("config.cfg", "r")
            if f:
                for i in f.readlines():
                    if "ENDPOINT_1" in i:
                        ep=i.split('=')[1]
                        if len(ep) > 1:
                            self.ep_1=ep.strip()
                    elif "ENDPOINT_2" in i:
                        ep=i.split('=')[1]
                        if len(ep) > 1:
                            self.ep_2=ep.strip()
                print ("Configured END points %s %s" % (self.ep_1, self.ep_2))
                f.close()
        def send2EP(self, url, data):
            r = requests.post(url=url, data=data) 
            server_statusCode = r.status_code
            print(r.text)

        def send(self,data):
            if self.ep_1 == None and self.ep_2 == None:
                print data
                return
            if self.ep_1 != None:
                self.send2EP(self.ep_1, data)
            if self.ep_2 != None:
                self.send2EP(self.ep_2, data)
