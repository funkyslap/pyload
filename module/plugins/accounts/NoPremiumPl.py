# -*- coding: utf-8 -*-

import datetime
import hashlib
import time

from module.common.json_layer import json_loads
from module.plugins.internal.Account import Account


class NoPremiumPl(Account):
    __name__    = "NoPremiumPl"
    __type__    = "account"
    __version__ = "0.02"

    __description__ = "NoPremium.pl account plugin"
    __license__     = "GPLv3"
    __authors__     = [("goddie", "dev@nopremium.pl")]


    API_URL   = "http://crypt.nopremium.pl"
    API_QUERY = {'site'    : "nopremium",
                 'username': ""         ,
                 'password': ""         ,
                 'output'  : "json"     ,
                 'loc'     : "1"        ,
                 'info'    : "1"        }

    _req = None
    _usr = None
    _pwd = None


    def loadAccountInfo(self, name, req):
        self._req = req
        try:
            result = json_loads(self.runAuthQuery())
        except Exception:
            # todo: return or let it be thrown?
            return

        premium = False
        valid_untill = -1

        if "expire" in result.keys() and result["expire"]:
            premium = True
            valid_untill = time.mktime(datetime.datetime.fromtimestamp(int(result["expire"])).timetuple())

        traffic_left = result["balance"] * 1024

        return {'validuntil' : valid_untill,
                'trafficleft': traffic_left,
                'premium'    : premium     }


    def login(self, user, data, req):
        self._usr = user
        self._pwd = hashlib.sha1(hashlib.md5(data["password"]).hexdigest()).hexdigest()
        self._req = req

        try:
            response = json_loads(self.runAuthQuery())
        except Exception:
            self.wrongPassword()

        if "errno" in response.keys():
            self.wrongPassword()

        data['usr'] = self._usr
        data['pwd'] = self._pwd


    def createAuthQuery(self):
        query = self.API_QUERY
        query["username"] = self._usr
        query["password"] = self._pwd
        return query


    def runAuthQuery(self):
        return self._req.load(self.API_URL, post=self.createAuthQuery())
