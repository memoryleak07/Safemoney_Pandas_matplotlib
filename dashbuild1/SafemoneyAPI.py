
import json
from csv import reader

import requests
import base64
from datetime import datetime
from requests.compat import urljoin
import pandas as pd
from io import StringIO

class SafemoneyAPI:

    myurl1 = 'http://'
    myurl2 = ':7409/'
    # headers = {
    #       'Authorization': 'Basic cGluOjExMTE=',
    #       'Content-Type': 'application/json'
    #     }

    def basicAuth(self, pin):
        pin = "pin:"+pin
        pin = pin.encode(encoding='utf8') 
        pin = base64.b64encode(pin).decode("utf-8")
        # pin = pin.decode("utf-8")
        headers = { 
            'Authorization': "Basic %s" % pin,
            'Content-Type': 'application/json' 
            }
        return headers


    def deviceStatus(self, ip, pin):
        command = "deviceStatus"
        try:
            response = requests.request("GET", url = urljoin(self.myurl1 + ip + self.myurl2, command), headers=self.basicAuth(pin), timeout=5)
            print(response.url)            
            if response.status_code == 200:
                res = json.loads(response.text)
                self.status = res["deviceStatus"]
                self.data = res["statusInfo"]
                if self.status == "OFFLINE":
                    i = 0
                    self.myres = []
                    for res["totalCount"] in self.data:
                        error = str(self.data[i]).find("""'InError': True""")
                        if error != -1:
                            print("\n", self.data[i])
                            self.err = self.data[i]["statusCode"]
                            self.myres.append(self.err)
                        i = i + 1
                    print(self.myres)

                    return str(self.myres)
                else:
                    print(self.status)
                    return str(self.status)
            else:
                print ("ERROR: ", response.status_code)
                return ("ERROR: ", response.status_code)
        except (requests.exceptions.HTTPError,requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as err:
            print ("ERROR: ", err)
            return ("ERROR: ", err)


    def getTransaction(self, ip, pin, datefrom, dateto):
        #http://192.168.70.14:7409/transactionslog?offset=0&limit=7&datefrom=2021-09-27&dateto=2021-09-27
        # print(datefrom, dateto)
        command = "transactionslog?"
        offset = 0
        limit = 100
        self.url = (self.myurl1 + ip + self.myurl2 + command) + "offset={offset}&limit={limit}&datefrom={datefrom}&dateto={dateto}".format(offset=offset,limit=limit,datefrom=datefrom,dateto=dateto)
        try: 
            response = requests.request("GET", self.url, headers=self.basicAuth(pin), timeout=15)
            # print(response.url)
            self.myres = []
            if response.status_code == 200:
                self.res = json.loads(response.text)
                totcount = self.res["totalCount"]
                self.myres.append(self.res)
                val = 0
                if totcount > limit:
                    for offset in range (val, totcount, limit):
                        self.url = (self.myurl1 + ip + self.myurl2 + command) + "offset={offset}&limit={limit}&datefrom={datefrom}&dateto={dateto}".format(offset=offset,limit=limit,datefrom=datefrom,dateto=dateto)
                        response = requests.request("GET", self.url, headers=self.basicAuth(pin), timeout=15)
                        self.response = json.loads(response.text)
                        transactionlog = self.response['transactionsLog']
                        self.myres.append(transactionlog)
                        offset =+ 100
                # df = pd.DataFrame([])            
                # df = (df["transactionsLog"].apply(pd.Series))
                # new_header = df.iloc[0] #grab the first row for the header
                # df = df[1:] #take the data less the header row
                # df.columns = new_header #set the header row as the df h
                # # df = df.drop(columns=['Id','Date','Token','ResCode','ResDescription','Levels','User',"Paid","Dispensed","Total", "Description"])
                self.myres = json.dumps(self.myres)
                # df = pd.DataFrame(list(reader(self.myres)))
                # df = (df["transactionsLog"].apply(pd.Series))
                # print(self.myres)
                return self.myres

            else:
                # print(response)
                return response
        except (requests.exceptions.HTTPError,requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as err:
            # print(err)
            return err


