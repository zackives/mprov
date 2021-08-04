'''
 Copyright 2021 Trustees of the University of Pennsylvania

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
'''
import asyncio
import base64
import pickle


class MProvServer:
    def __init__(self):
        asyncio.create_task(self.main())


    async def handle(self, reader, writer):
        data = await reader.readline()
        decoded = base64.b64decode(data)
        message = pickle.loads(decoded)

        writer.close()

    async def main(self):
        server = await asyncio.start_server(self.handle, '127.0.0.1', 8088)

        addr = server.sockets[0].getsockname()
        print(f'MProvServer serving on {addr}')

        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    s = MProvServer()
    print('Server created')
