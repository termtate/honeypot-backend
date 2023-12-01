import asyncio


async def send():
    _, writer = await asyncio.open_connection("localhost", 8123)
    message = '''<Root>
        <SYMBOL>20</SYMBOL>
        <AlertType>1</AlertType>
        <SubType>1</SubType>
        <Time>2023-01-01-00-00-00-00</Time>
        <Proto>1</Proto>
        <sPort>8888</sPort>
        <dPort>8112</dPort>
        <ConnectBeginTime>2023-01-01-00-00-00-00</ConnectBeginTime>
        <receiveTime>1</receiveTime>
        <PacketLen>1</PacketLen>
        <ip_src>0.0.0.0</ip_src>
        <ip_dst>1.1.1.1</ip_dst>
    </Root>'''
    writer.write(message.encode())
    await writer.drain()
    print("send message")
    writer.close()
    await writer.wait_closed()


async def main():
    while True:
        await send()
        await asyncio.sleep(2)


asyncio.run(main())
