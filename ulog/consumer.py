# -*- coding: utf-8 -*-

import time
import urllib

class ULogException(Exception):
  """ ULogException represents a domain exception returned by a call to ULog. Exceptions have a type and a message """
  def __init__(self, _type, message):
    super(ULogException, self).__init__("{0}: {1}".format(_type, message))
    self.type, self.message = _type, message


class Consumer:
  """Consumer exposes all the operations that read information from ULog"""

  def __init__(self, client):
    self.client = client


  def search_streams(self, pattern=None):
    """ search_streams returns a list of stream names matching a given pattern """
    p = {"matching": pattern} if pattern is not None else {}
    r = self.client.get("/streams", params=p)
    self.handle_errors(r)

    return r.json()


  def describe_stream(self, stream):
    """ describe_stream returns detailed information about a particular stream """
    r = self.client.get("/streams/{0}".format(stream))
    self.handle_errors(r)

    return r.json()


  def describe_stream_partition(self, stream, partition):
    """ describe_stream_partition returns detailed information about a particular partition within a stream """
    r = self.client.get("/streams/{0}/partitions/{1}".format(stream, partition))
    self.handle_errors(r)

    return r.json()

  
  def read_from(self, stream, partition, _from=None, _to=None):
    """ 
    read_from returns a generator that yields all events between the specified offsets of the provided stream partition.
    If _from is not specified, it starts from the oldest event in the stream partition
    If _to is not specified, it finishes when it reaches the newest event in the stream partition
    """
    # Set (from, to) parameters depending on their availability
    params = urllib.urlencode({k: v for k, v in (('from', _from), ('to', _to)) if v is not None})

    next_page = "/streams/{0}/partitions/{1}/events?{2}".format(stream, partition, params)
    while next_page != "":
      r = self.client.get(next_page)
      self.handle_errors(r)
      results = r.json()

      for event in results["events"]:
        yield event

      next_page = results["next_page_url"]


  def subscribe_to(self, stream, partition, _from=None, refresh_period=2):
    """ 
    subscribe_to returns a generator that yields all (old and new) events from the provided stream partition.
    If _from is not specified, it starts from the oldest event in the stream partition
    """
    # Set (from, to) parameters depending on their availability
    params = {"from": _from} if _from is not None else {}

    while True:
      r = self.client.get("/streams/{0}/partitions/{1}/events".format(stream, partition), params=params)
      results = r.json()

      # If there were no events, wait for a few seconds
      if r.status_code == 400 and results["type"] == "OffsetOutOfBounds":
        time.sleep(refresh_period)
        continue

      # Otherwise, check if there was an error with the request
      self.handle_errors(r)

      # Finally, yield all new events and prepare for the next request
      for event in results["events"]:
        last_offset_yielded = event["offset"]
        yield event

      params["from"] = last_offset_yielded + 1


  def handle_errors(self, response):
    """ handle_errors is responsible for raising the appropriate exceptions for bad requests """
    if response.status_code == 400:
      error = response.json()
      raise ULogException(error["type"], error["message"])
    elif response.status_code > 400:
      response.raise_for_status()

