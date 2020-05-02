import time
import json
import traceback
import asyncio
import async_timeout
import aiohttp

import logging

formatter = '{"level": %(levelname)s", "timestamp": "%(asctime)s", "phase": "fetcher", "contents": %(message)s}'
logging.basicConfig(format=formatter, level=logging.INFO)

logger = logging.getLogger(__name__)



class Response:
    def __init__(self, status=None, headers=None, body=None):
        self.status = status
        self.headers = headers
        self.body = body

class Request:
    def __init__(self, url=None, method=None, headers=None, payload=None, meta=None, retry_num=3, response=Response()):
        self.url = url
        self.method = method
        self.headers = headers
        self.payload = payload
        self.meta = meta
        self.response = response
        self.retry_num = retry_num
        self.retry_flag = False

    def set_response(self, response):
        if not isinstance(response, Response):
            return None

        self.response = response
        return True

    def set_retry(self):
        self.retry_num -= 1
        self.retry_flag = True

    def disable_retry(self):
        self.retry_flag = False


class Fetcher:
    def __init__(self, timeout=30):
        self.timeout = timeout

    def flow(self, requests):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.__gather(requests))

    async def __gather(self, requests):
        async with aiohttp.ClientSession() as session:
            promises = [asyncio.ensure_future(self.aiofetch(session, request)) for request in requests]
            if len(promises) == 0:
                return []
            return await asyncio.gather(*promises)

    async def aiofetch(self, session, request):
        async with async_timeout.timeout(int(self.timeout)):
            status = None
            headers = None
            body = None

            try:
                if request.method.lower() == "get":
                    async with session.get(request.url, data=request.payload) as ares:
                        status = ares.status
                        headers = ares.headers
                        body = await ares.text()

                if request.method.lower() == "post":
                    async with session.post(request.url, data=request.payload) as ares:
                        status = ares.status
                        headers = ares.headers
                        body = await ares.text()


                logger.info(json.dumps({'code': status, 'request_method': 'get', 'request_url': request.url}))

                if status == 404 or status == 500:
                    request.set_retry()
                elif status == 200:
                    request.disable_retry()


            except:
                err_body = json.dumps({
                  "error" : {
                    "timestamp": int(time.time()),
                    "msg": "Failed request, 'req_method: {}', 'req_url: {}', 'traceback: {}'".format(
                        request.method,
                        request.url,
                        traceback.format_exc()
                    )
                  }
                })

                logger.error(err_body)

            finally:
                response = Response(status=status, headers=headers, body=body)
                request.set_response(response)
                return request
