# Chat application using asyncio.

* TCP server with asyncio's `start_server()`.
* Server runs on `localhost` or `0.0.0.0`. 
* Multiple clients connect and send unlimited messages to each other.

Original attempt used threading and socket libraries, but switched to higher level `asyncio` using `streamReader` and `streamWriter`.

To replace the thread that handled STDin from each client, the external library `aioconsole` was installed. This allowed concurent receving of messages and waiting for input with `msg = await ainput()`.

## Data Transfer

### Sending Data

Sending messages over a continuous TCP connetion was done using Python's `struct` library. Messages are prefixed with the size of the message in a constant format.
```python
# Get message from STDin
msg = await ainput()
msg = msg.encode()

# prefix the message with the length of the message
# using network (big-endian) encoding (!) of an unsigned long (L)
size = pack('!L',len(msg))
writer.write(size)
writer.write(msg)
await writer.drain()
```

### Receiving Data
Receiving data is then done by first getting the size of the payload, then reading that amount of bytes.
The following snippet is inside a `while True` loop that breaks when no more data is sent, i.e. the connection is closed.
```python
try:
    # read exactly 4 bytes to get size of message (size of long)
    # size is prefixed in every client message
    size = await reader.readexactly(4)
  except asyncio.IncompleteReadError:
    break

  # unpack size of payload as network (big-endian) unsigned long
  size, = unpack('!L',size)

  # read message
  msg = await reader.readexactly(size)
  print(f'{msg.decode()}')
  ```
