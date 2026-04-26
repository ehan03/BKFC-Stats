# standard library imports

# third party imports
from scrapy.spiders import Spider

# local imports
from ..items.bkfc_items import BKFCFighterItem


class BKFCFighterSpider(Spider):
    name = "bkfc_fighter_spider"
    allowed_domains = ["bkfc.com"]
    start_urls = ["https://www.bkfc.com/fighters"]
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "CONCURRENT_REQUESTS": 4,
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
            "scrapy_bkfc.pipelines.bkfc_pipelines.BKFCFighterPipeline": 100,
        },
        "CLOSESPIDER_ERRORCOUNT": 1,
    }

    def parse(self, response):
        # Get all fighter links
        fighter_links = response.css("a.fighter-card::attr(href)").getall()
        fighter_names = response.css("a.fighter-card::attr(data-event-label)").getall()

        # Crawl fighter pages and extract info
        assert len(fighter_links) == len(fighter_names)
        for link, name in zip(fighter_links, fighter_names):
            url = response.urljoin(link)
            yield response.follow(
                url, callback=self.parse_fighter, cb_kwargs={"name": name}
            )

        # Follow pagination
        next_page = response.css("a.w-pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(response.urljoin(next_page), callback=self.parse)

    def parse_fighter(self, response, name):
        # Create fighter item
        fighter_item = BKFCFighterItem()

        slug = response.url.rstrip("/").split("/")[-1]
        fighter_item["slug"] = slug
        fighter_item["name"] = name or response.css("h1.hero_heading::text").get()

        # Record
        wins = response.css(
            ".hero_record_item:nth-child(1) .hero_record_number:not(.w-condition-invisible)::text"
        ).get()
        losses = response.css(
            ".hero_record_item:nth-child(3) .hero_record_number:not(.w-condition-invisible)::text"
        ).get()
        draws = response.css(
            ".hero_record_item:nth-child(5) .hero_record_number:not(.w-condition-invisible)::text"
        ).get()
        fighter_item["wins"] = int(wins)
        fighter_item["losses"] = int(losses)
        fighter_item["draws"] = int(draws)

        # Stats
        def get_stat_item(label):
            """
            Return the <li> node corresponding to a stat label
            """
            for li in response.css(".stat_list-item"):
                lbl = li.css(".stat_list-item_label::text").get("")
                if label.lower() in lbl.lower():
                    return li
            return None

        # --- division ---
        division = None
        li = get_stat_item("Division")
        if li:
            division = li.css("p:not(.stat_list-item_label)::text").get()
            if division:
                division = division.strip()

        # --- reach ---
        reach = None
        li = get_stat_item("Reach")
        if li:
            reach = li.css("p:not(.stat_list-item_label)::text").get()
            if reach:
                reach = reach.strip()

        # --- height (handle imperial vs metric duplication) ---
        height = None
        li = get_stat_item("height")
        if li:
            # Prefer imperial if available
            height = li.css("[data-height-imperial]::text").get()

            if not height:
                height = li.css("[data-height]::text").get()

            if height:
                height = height.strip()

        # --- nickname ---
        nickname = None
        li = get_stat_item("nickname")
        if li:
            nickname = li.css("p:not(.stat_list-item_label)::text").get()
            if nickname:
                nickname = nickname.strip()

        # --- dob (really birth date, not displayed age) ---
        dob = None
        li = get_stat_item("age")
        if li:
            # hidden but actual useful value
            dob = li.css("[data-birth]::text").get()

            if dob:
                dob = dob.strip()
                if dob == "--":
                    dob = None

        # --- nationality ---
        nationality = None
        li = get_stat_item("Nationality")
        if li:
            nationality = li.css(".fighters_nation p::text").get()
            if nationality:
                nationality = nationality.strip()

        fighter_item["division"] = division
        fighter_item["reach"] = reach
        fighter_item["height"] = height
        fighter_item["nickname"] = nickname
        fighter_item["dob"] = dob
        fighter_item["nationality"] = nationality

        # Social media links
        socials = response.css(".girls_card_socials a[href]::attr(href)").getall()
        socials = [s for s in socials if s and s != "#"]
        social_media = "; ".join(socials) if socials else None
        fighter_item["social_media"] = social_media

        yield fighter_item
