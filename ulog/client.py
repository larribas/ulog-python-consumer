# -*- coding: utf-8 -*-

import requests

class Client:
  """Encapsulates the client configuration the consumer will use to communicate with the ULog instance"""

  def __init__(self, host, port, token):
    self.base_url = "%s:%s" % (host, port)
    self.session = requests.Session()
    self.session.headers['Authorization'] = token

  def get(self, url, **kwargs):
    return self.session.get(self.base_url + url, **kwargs)
