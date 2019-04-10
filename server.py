import asyncio
import websockets

class SensorDataServer:
    def __init__(self):
        self.sensor_data = []

    async def hello(websocket, path):
        # Wait for a connection
        data = await websocket.recv()
        self.sensor_data.append(data)
        print(f"< {data}")

        response = f"Received {data}!"
        await websocket.send(response)
        print(f"> {response}")

server = SensorDataServer()
start_server = websockets.serve(server.hello, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
