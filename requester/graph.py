import sys
import time
import argparse
import configparser
from .schedule import Schedule
from .pipeline import Pipeline
from .http import Request, Fetcher

import logging

formatter = '{"level": %(levelname)s", "timestamp": "%(asctime)s", "place": %(name)s, "contents": %(message)s}'
logging.basicConfig(format=formatter, level=logging.INFO)

logger = logging.getLogger(__name__)

class Requester:
    def __init__(self, ctx=None, settings=None, schedule=None, fetcher=None, pipeline=None):
        if ctx:
            assert isinstance(ctx, dict), "Invalid ctx type, dict was expected"

        args = helper_args()
        if settings:
            assert isinstance(settings, dict), "Invalid settings type, dict was expected"
        else:
           settings, section = helper_settings(args)

        self.ctx = ctx
        self.settings = settings

        #MEMO: modify when some settings add to here
        if not self.settings:
            self.throttle = 5
            self.concurrent_num = 20
            self.async_pipeline = None
        else:
            self.throttle = settings.getint(section, 'throttle')
            self.concurrent_num = settings.getint(section, 'concurrent_num')
            self.async_pipeline = settings.getboolean(section, 'async_pipeline')

        self.schedule = schedule or Schedule(ctx=self.ctx, concurrent_num=self.concurrent_num)
        self.fetcher = fetcher or Fetcher(ctx=self.ctx)
        self.pipeline = pipeline or Pipeline(ctx=self.ctx, async_on=self.async_pipeline)


    def source_scheduling(self):
        shedule_obj = self.schedule
        queues = shedule_obj.source_flow()
        return queues


    def flow_fetcher(self, scheduled_queues):
        queues = (q for q in scheduled_queues if q)
        return self.fetcher.flow(queues)


    def flow_pipeline(self, responses):
        pipeline_obj = self.pipeline
        return pipeline_obj.flow(responses)


    def aflow_pipeline(self, responses):
        pipeline_obj = self.pipeline
        return pipeline_obj.aflow(responses)


    def sink_scheduling(self, responses):
        return self.schedule.sink_flow(responses)


    def __graph(self):
        sheduled_queues = self.source_scheduling()

        responses = self.flow_fetcher(sheduled_queues)
        if len(responses) == 0:
            return self.sink_scheduling(responses)

        if self.async_pipeline:
            shedulings = self.aflow_pipeline(responses)
        else:
            shedulings = self.flow_pipeline(responses)

        continius = self.sink_scheduling(shedulings)
        return continius

    def run(self):
        while self.__graph():
            logger.info("running requester")
            time.sleep(self.throttle)

def helper_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--path-conf-ini',
        action='store',
        nargs='?',
        help='Specify .ini file path'
    )

    parser.add_argument('-s','--conf-ini-section',
        action='store',
        nargs='?',
        default="default",
        help='Specify use section ini'
    )
    return parser.parse_args()

def helper_settings(args):
    c_path = args.path_conf_ini
    c = configparser.ConfigParser()
    c.read(c_path)
    if len(c.sections()) == 0:
        return None

    return (c, args.conf_ini_section)
