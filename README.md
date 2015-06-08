# ULog Python Consumer

This library provides a powerful interface to consume events from a ULog cluster, in a pythonic way.


## Usage Examples

### Searching for streams and inspecting particular details

```python
import ulog
client = ulog.Client('http://localhost', '80', token='Acngqr8chd')
consumer = ulog.Consumer(client)

all_streams = c.search_streams()
certain_streams = c.search_streams('^some-str(.)*$')

info_about_a_stream = consumer.describe_stream('some-stream')
info_about_a_partition = consumer.describe_stream_partition('some-stream', partition=0)

```


### Reading a series of events from a stream partition

You can easily read a series of events from a partition. Calling `read_from` returns a [generator](https://wiki.python.org/moin/Generators). The generator will yield each event on demand. Internally, it will make all necessary requests to ULog (due to paginated results), just-in-time (that is, just before an event from the next page is requested).

```python
import ulog
client = ulog.Client('http://localhost', '80', token='Acngqr8chd')
consumer = ulog.Consumer(client)

# from= and to= parameters may be omitted, meaning the oldest and newest available, respectively
event_generator = consumer.read_from('some-stream', from=1000, to=2000)
for x in event_generator:
  if x["event"]["type"] == "NewFacebookUser":
    send_marketing_email(x["event"]["content"]["user"]["email"])

```


### Subscribing to new events from a stream partition

You can subscribe to a partition's events, and receive them as they come. Calling `subscribe_to` returns a generator (see previous section). Internally, the consumer polls ULog for new events at certain time intervals (configurable via the `refresh_period` parameter, which is 2 seconds by default).

N.B. Waiting for the next event may block the program's execution.

```python
import ulog
client = ulog.Client('http://localhost', '80', token='Acngqr8chd')
consumer = ulog.Consumer(client)

# from= may be provided. If omitted, it subscribes from the oldest offset available
# a custom refresh_period= may be specified (e.g. refresh_period=0.5 to wait half a second to issue the next request)
event_generator = consumer.subscribe_to('some-stream')
for x in event_generator:
  do_something_with(x["event"])

# ...

@asyncio.coroutine
def do_something_with(event):
  # process the event in a different routine
  pass

```


