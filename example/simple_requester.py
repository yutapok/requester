from requester.graph import Requester
from requester.schedule import Schedule
from requester.pipeline import Pipeline

class SimpleSchedule(Schedule):
    urls = [
      'http://www.sample1.com',
      'http://www.sample2.com',
    ]
    def source(self):
        for _ in range(self.concurrent_num):
            url = urls.pop()
            yield {'url': url, 'method': 'get'}

    def sink(self, response):
        for res in responses:
            if res.status == 200
                continue

            yield res

class SimplePipeline(Pipeline):
    def processor(self, response):
        print(response.body)
        return response


if __name__ == '__main__':
    requester = Requester(
        schedule=SimpleSchedule(),
        pipeline=SimplePipeline()
    )

    requester.run()
