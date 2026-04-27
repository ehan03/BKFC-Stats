# standard library imports
import json
import os

# third party imports
import pandas as pd
from dotenv import load_dotenv
from scrapy import Request
from scrapy.spiders import Spider

# local imports

load_dotenv()
COMBATREG_API_KEY = os.getenv("COMBATREG_API_KEY")


class CombatRegistryMetaSpider(Spider):
    name = "combatreg_meta_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "CONCURRENT_REQUESTS": 1,
        "COOKIES_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
        },
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "FEED_EXPORT_ENCODING": "utf-8",
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
        "RETRY_TIMES": 0,
        "LOG_LEVEL": "INFO",
        "ITEM_PIPELINES": {
            "scrapy_bkfc.pipelines.combatreg_pipelines.CombatRegistryMetaPipeline": 100,
        },
        "CLOSESPIDER_ERRORCOUNT": 1,
        "DOWNLOAD_DELAY": 1.5,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.5,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
    }

    def start_requests(self):
        promoter_id = "dfdc3cfa-28c1-4bde-a601-31fc8caa83a3"

        url = f"https://xapi.mmareg.com/events/past/detailed?promoter_ids={promoter_id}"

        yield Request(
            url,
            headers={
                "X-Api-Key": COMBATREG_API_KEY,
                "Accept": "application/json",
            },
            callback=self.parse,
            meta={"offset": 0, "promoter_id": promoter_id},
        )

    def parse(self, response):
        data = json.loads(response.text)

        if len(data) > 0:
            yield data
        else:
            return

        offset = response.meta["offset"]
        promoter_id = response.meta["promoter_id"]
        next_offset = offset + len(data)

        next_url = (
            f"https://xapi.mmareg.com/events/past/detailed"
            f"?promoter_ids={promoter_id}&offset={next_offset}"
        )

        yield Request(
            next_url,
            headers={
                "X-Api-Key": COMBATREG_API_KEY,
                "Accept": "application/json",
            },
            callback=self.parse,
            meta={
                "offset": next_offset,
                "promoter_id": promoter_id,
            },
        )


class CombatRegistryEventStatsSpider(Spider):
    name = "combatreg_event_stats_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "CONCURRENT_REQUESTS": 1,
        "COOKIES_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
        },
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "FEED_EXPORT_ENCODING": "utf-8",
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
        "RETRY_TIMES": 0,
        "LOG_LEVEL": "INFO",
        "ITEM_PIPELINES": {
            "scrapy_bkfc.pipelines.combatreg_pipelines.CombatRegistryEventStatsPipeline": 100,
        },
        "CLOSESPIDER_ERRORCOUNT": 1,
        "DOWNLOAD_DELAY": 0.5,
    }

    def start_requests(self):
        dir_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "raw",
            "combatreg",
        )
        mapping_df = pd.read_csv(os.path.join(dir_path, "manual_mapping.csv"))
        ids = mapping_df.loc[
            mapping_df["final_stats_id"].notnull(), "final_stats_id"
        ].values.tolist()
        ids = [int(id) for id in ids]  # type: ignore

        for id in ids:
            url = f"https://xapi.mmareg.com/api/v2/bkfc/?type=json&modifier=event-stats&id={id}"
            yield Request(
                url,
                callback=self.parse,
            )

    def parse(self, response):
        data = json.loads(response.text)

        yield data


class CombatRegistryFighterSpider(Spider):
    name = "combatreg_fighter_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 6,
        "CONCURRENT_REQUESTS": 6,
        "COOKIES_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 400,
        },
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "FEED_EXPORT_ENCODING": "utf-8",
        "DEPTH_PRIORITY": 1,
        "SCHEDULER_DISK_QUEUE": "scrapy.squeues.PickleFifoDiskQueue",
        "SCHEDULER_MEMORY_QUEUE": "scrapy.squeues.FifoMemoryQueue",
        "RETRY_TIMES": 0,
        "LOG_LEVEL": "INFO",
        "CLOSESPIDER_ERRORCOUNT": 1,
    }

    def start_requests(self):
        dir_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "raw",
            "combatreg",
        )

        with open(os.path.join(dir_path, "metadata.json"), "r", encoding="utf-8") as f:
            metadata = json.load(f)

        fighter_uuids = []
        for event in metadata:
            fights = event["fights"]
            for fight in fights:
                fighters = fight["fighters"]
                for fighter in fighters:
                    fighter_uuids.append(fighter["uuid"])

        fighter_uuids = list(set(fighter_uuids))
        for uuid in fighter_uuids:
            url = f"https://xapi.mmareg.com/fighters/{uuid}/basic"

            yield Request(
                url,
                headers={
                    "X-Api-Key": COMBATREG_API_KEY,
                    "Accept": "application/json",
                },
                callback=self.parse,
            )

    def parse(self, response):
        data = json.loads(response.text)

        yield data

        # Find opponents and crawl them too
        fights_history = data["fights_history"]
        fighter_uuids = []
        for fight in fights_history:
            fighters = fight["fighters"]
            for fighter in fighters:
                fighter_uuids.append(fighter["uuid"])

        fighter_uuids = list(set(fighter_uuids))
        for uuid in fighter_uuids:
            url = f"https://xapi.mmareg.com/fighters/{uuid}/detailed"

            yield Request(
                url,
                headers={
                    "X-Api-Key": COMBATREG_API_KEY,
                    "Accept": "application/json",
                },
                callback=self.parse,
            )
