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
import pickle
import base64



class MProvClient:

    def __init__(self):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = None

    async def tcp_echo_client(self, message):
        _, self.writer = await asyncio.open_connection('127.0.0.1', 8088)

        self.writer.write(message)
        self.writer.close()

    def submit_value(self, value):
        pickled = pickle.dumps(value)
        m = base64.b64encode(pickled) + b'\n'
        if self.loop and self.loop.is_running():
            self.loop.create_task(self.tcp_echo_client(m))
        else:
            asyncio.run(self.tcp_echo_client(m))


if __name__ == '__main__':
    c = MProvClient()
    c.submit_value(['one', 1, None])
    c.submit_value(['two', 2, None])
    c.submit_value(['three', 3, None])
    c.submit_value([('a', 1, None), ('b', 2, None), ('c', 3, None)])
