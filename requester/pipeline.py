import json
import traceback
import asyncio

import logging

formatter = '{"level": %(levelname)s", "timestamp": "%(asctime)s", "phase": "pipeline", "contents": "%(message)s}"'
logging.basicConfig(format=formatter, level=logging.INFO)

logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, ctx=None, async_on=None):
        self.ctx = ctx
        self.async_on = async_on

    def processor(self, response):
        """Notice: override this method"""
        return

    async def aprocessor(self, response):
        """Notice: override this method"""
        return

    def __processor(self, response):
        try:
            return self.processor(response)
        except:
            err_body = json.dumps({
              "error" : {
                "msg": "Failed to process response, 'traceback: {}'".format(
                    traceback.format_exc()
                )
              }
            })

            logger.error(err_body)
            return response

    async def __aprocessor(self, response):
        try:
            return await self.aprocessor(response)
        except:
            err_body = json.dumps({
              "error" : {
                "msg": "Failed to process response, 'traceback: {}'".format(
                    traceback.format_exc()
                )
              }
            })

            logger.error(err_body)
            return response


    def flow(self, responses):
        pipes = (self.__processor(response) for response in responses)
        for pipe in pipes:
            yield pipe


    def aflow(self, responses):
        loop_pipe = asyncio.get_event_loop()
        return loop_pipe.run_until_complete(self.gather(responses))


    async def gather(self, responses):
        promises = [asyncio.ensure_future(self.__aprocessor(response)) for response in responses]
        return await asyncio.gather(*promises)
