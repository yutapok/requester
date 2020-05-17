from .http import Request

import logging

logger = logging.getLogger(__name__)

class Schedule:
    def __init__(self, ctx=None, run_forever=False, concurrent_num=1):
        self.ctx = ctx if isinstance(ctx, dict) else None
        self.queue_store = []
        self.run_forever = run_forever
        self.concurrent_num = concurrent_num

    def __get_schedule(self):
        c = len(self.queue_store) if len(self.queue_store) < self.concurrent_num else self.concurrent_num
        for q in range(c):
            yield self.queue_store.pop()

    def __set_schedule(self, queue):
        self.queue_store.append(queue)

    def is_continius(self):
        if len(self.queue_store) > 0:
            return True

        return False

    def source_flow(self):
        arr = self.source()
        if not arr:
            return self.__get_schedule()

        for q in arr:
            assert isinstance(q, dict), "Invalid data type, source must prepare 'dict'"
            if len(q) <= 0:
                continue
            request_queue = Request(
                url=q['url'],
                method=q['method'],
                headers=q.get("headers"),
                payload=q.get("payload"),
                meta=q.get('meta')
            )
            self.__set_schedule(request_queue)

        return self.__get_schedule()

    def sink_flow(self, responses):
        arr = self.sink(responses)
        if not arr:
            return False

        for q in arr:
            assert isinstance(q, Request), "Invalid data type, source must prepare 'Request'"

            if q.retry_flag and q.retry_num == 0:
                continue

            if q.retry_flag and q.retry_num > 0:
                logger.warning("retry request, url: '{}', left retry count '{}'".format(q.url, q.retry_num))

            self.__set_schedule(q)

        if self.run_forever:
            return True

        if len(self.queue_store) == 0:
            return False

        return True

    def source(self):
        """Notice: override this class"""
        yield {}

    def sink(self, responses):
        """Notice: override this class"""
        yield
