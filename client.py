import asyncio
import sys
from struct import pack, unpack
from aioconsole import ainput

HOST, PORT = "10.0.0.57", 8080

async def init_name(writer):
    name = sys.argv[1]

    name = name.encode()
    size = pack('!L',len(name))
    writer.write(size)
    writer.write(name)
    await writer.drain()

    print('Connected to server')


async def send_messages(writer):
    
    
    await init_name(writer)

    msg = await ainput()
    while msg != 'q':
        msg = msg.encode()

        # prefix the message with the length of the message
        # using network (big-endian) encoding (!) of an unsigned long (L)
        size = pack('!L',len(msg))
        writer.write(size)
        writer.write(msg)
        await writer.drain()

        # prevent blocking from input(). asynchronously get STDIN
        msg = await ainput()

    print('Disconnecting from server.')
    writer.close()


async def receive_messages(reader):
    while True:
        try:
            # read exactly 4 bytes to get size of message
            # size is prefixed in every client message
            size = await reader.readexactly(4)
        except asyncio.IncompleteReadError:
            break

        # unpack size of payload as network (big-endian) unsigned long
        size, = unpack('!L',size)
        #print(f'size: {size}')
        
        # read message
        msg = await reader.readexactly(size)
        print(f'{msg.decode()}')

        

async def connect_to_server():
    reader, writer = await asyncio.open_connection(HOST, PORT)


    await asyncio.gather(
        send_messages(writer), 
        receive_messages(reader))

if __name__ == "__main__":
    asyncio.run(connect_to_server())