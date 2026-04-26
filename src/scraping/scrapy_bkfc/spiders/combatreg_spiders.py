# standard library imports
import json
import os

# third party imports
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
