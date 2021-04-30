import asyncio
from struct import unpack, pack

HOST, PORT = "0.0.0.0", 8080

clients = {}

async def broadcast(writer, size, msg):
    for client in clients.values():
        if client != writer:
            client.write(size)
            client.write(msg)
            await client.drain()



async def handle_client(reader, writer):

    # addr is tuple for the socket family
    # AF_INET6: (host, port, flowinfo, scope_id)
    # AF_INET (4): (host, port) 
    addr = writer.get_extra_info('peername')
    print(f'Client connected from: {addr}')




    try:
        packed_size = await reader.readexactly(4)
    except asyncio.IncompleteReadError:
        print("Error initializing client name")
        return
    
    # unpack size of payload as network (big-endian) unsigned long
    size, = unpack('!L',packed_size)
    print(f'size of name: {size}')
    
    # read message
    name = await reader.readexactly(size)
    name = name.decode()
    print(f'client name: {name}')

    clients[name] = writer

    conn_msg = f'{name} just connected!'
    conn_msg = conn_msg.encode()
    conn_msg_size = pack('!L',len(conn_msg))
    await broadcast(writer, conn_msg_size, conn_msg)


################ ----- Begin loop
    while True:
        try:
            # read exactly 4 bytes to get size of message
            # size is prefixed in every client message
            packed_size = await reader.readexactly(4)
        except asyncio.IncompleteReadError:
            break

        # unpack size of payload as network (big-endian) unsigned long
        size, = unpack('!L',packed_size)
        print(f'size: {size}')
        
        # read message
        msg = await reader.readexactly(size)
        print(f'content: {msg.decode()}')

        await broadcast(writer, packed_size, msg)
    
    print('Client disconnected.')
    writer.close()
    clients.pop(name)


async def run_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f'Server running on: {server.sockets[0].getsockname()}')
    
    async with server:
        await server.serve_forever()
try:
    asyncio.run(run_server())
except KeyboardInterrupt:
    print('Closing Server.')
    pass