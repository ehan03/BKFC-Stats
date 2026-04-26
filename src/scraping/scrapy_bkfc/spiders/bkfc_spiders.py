# standard library imports
import html
import re

# third party imports
from scrapy.spiders import Spider

# local imports
from ..items.bkfc_items import BKFCBoutItem, BKFCEventItem, BKFCFighterItem


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


class BKFCEventSpider(Spider):
    name = "bkfc_event_spider"
    allowed_domains = ["bkfc.com"]
    start_urls = ["https://www.bkfc.com/event-past/past"]
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
            "scrapy_bkfc.pipelines.bkfc_pipelines.BKFCEventPipeline": 100,
        },
        "CLOSESPIDER_ERRORCOUNT": 1,
    }

    def parse(self, response, page=1):
        cards = response.css(".div-block-3")
        event_links = [card.css("a.w-inline-block::attr(href)").get() for card in cards]
        event_names = [card.css("h3.events_card_heading::text").get() for card in cards]

        assert len(event_links) == len(event_names)
        for position, (link, name) in enumerate(zip(event_links, event_names), start=1):
            url = response.urljoin(link)
            yield response.follow(
                url,
                callback=self.parse_event,
                cb_kwargs={"name": name, "page": page, "position": position},
            )

        next_page = response.css("a.w-pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(
                response.urljoin(next_page),
                callback=self.parse,
                cb_kwargs={"page": page + 1},
            )

    def parse_event(self, response, name, page, position):
        event_item = BKFCEventItem()

        event_slug = response.url.rstrip("/").split("/")[-1]
        event_item["slug"] = event_slug
        event_item["name"] = name
        event_item["page"] = page
        event_item["page_position"] = position

        # Date and location
        datetime_est = response.css("[data-event-date-est]::text").get("").strip()
        venue = (
            response.css(".hero-event-card_meta .text-size-1-25::text").get("").strip()
        )
        event_item["datetime_est"] = datetime_est if datetime_est else None
        event_item["venue"] = venue if venue else None

        # Stats IDs, for Combat Registry linkage
        script_text = response.css("script:not([src])").getall()
        combined = "\n".join(script_text)

        live_stats_id = None
        final_stats_id = None

        live_match = re.search(r"const LIVE_STATS\s*=\s*'([^']*)'", combined)
        final_match = re.search(r"const FINAL_STATS\s*=\s*'([^']*)'", combined)

        if live_match and live_match.group(1).strip():
            url = html.unescape(live_match.group(1))
            id_match = re.search(r"[?&]id=(\d+)", url)
            if id_match:
                live_stats_id = int(id_match.group(1))

        if final_match and final_match.group(1).strip():
            url = html.unescape(final_match.group(1))
            id_match = re.search(r"[?&]id=(\d+)", url)
            if id_match:
                final_stats_id = int(id_match.group(1))

        event_item["live_stats_id"] = live_stats_id
        event_item["final_stats_id"] = final_stats_id

        yield event_item

        # Extract bout info
        bouts = []

        def slug(node):
            if node is None:
                return None
            href = node.attrib.get("href", "")
            return href.rstrip("/").split("/")[-1] or None

        def get_corner(headshot_node):
            if headshot_node is None:
                return None
            win_label = headshot_node.css("[data-cond-key][data-cond-value='win']")
            if win_label:
                key = win_label.attrib.get("data-cond-key", "")
                if key == "BlueResult":
                    return "blue"
                if key == "RedResult":
                    return "red"
            return None

        def parse_physicals(cell):
            weight_kg = cell.css("p.weight-kg::text").get("").strip()
            height_raw = cell.css("p.height-m::text").get("").strip()
            return (
                float(weight_kg) if weight_kg else None,
                float(height_raw) if height_raw else None,
            )

        def parse_fist(cell):
            sizes = [
                s.strip()
                for s in cell.css(
                    "p.fist-size:not(.w-condition-invisible)::text"
                ).getall()
                if s.strip() and s.strip() != "--"
            ]
            return f"{sizes[0]}{sizes[1]}" if len(sizes) >= 2 else None

        for tab in response.css(".events_tab-content[data-w-tab]"):
            card_name = tab.attrib.get("data-w-tab", "")

            for wrapper in tab.css("[data-bout]"):
                card = wrapper.css(".fight-card")

                headshots = card.css("a.fight-card_headshot")
                f1_headshot = headshots[0] if len(headshots) > 0 else None
                f2_headshot = headshots[1] if len(headshots) > 1 else None

                f1_corner = get_corner(f1_headshot)
                f2_corner = get_corner(f2_headshot)
                assert f1_corner is not None and f2_corner is not None
                assert f1_corner != f2_corner

                blue_uuid = wrapper.attrib.get("data-athleteblueuuid")
                red_uuid = wrapper.attrib.get("data-athletereduuid")
                f1_uuid = blue_uuid if f1_corner == "blue" else red_uuid
                f2_uuid = blue_uuid if f2_corner == "blue" else red_uuid

                headings = card.css(
                    ".fight-card_header h3.fight-card_heading, .flex-aign-centerr h3.fight-card_heading"
                )
                assert len(headings) == 2
                bout_type = headings[0].css("::text").get("").strip() or None
                division = headings[1].css("::text").get("").strip() or None

                record_items = card.css(
                    ".fight-card_list-item:not(.hide-tablet):not(.is--results):not(.fight-card_buttons)"
                )

                # Height / weight
                height_row = record_items[1] if len(record_items) > 1 else None
                height_cells = (
                    height_row.css(".display-inlineflex") if height_row else []
                )
                f1_weight, f1_height = (
                    parse_physicals(height_cells[0])
                    if len(height_cells) > 0
                    else (None, None)
                )
                f2_weight, f2_height = (
                    parse_physicals(height_cells[2])
                    if len(height_cells) > 2
                    else (None, None)
                )

                # Fist size
                fist_row = record_items[2] if len(record_items) > 2 else None
                fist_cells = fist_row.css(".display-inlineflex") if fist_row else []
                f1_fist_size = (
                    parse_fist(fist_cells[0]) if len(fist_cells) > 0 else None
                )
                f2_fist_size = (
                    parse_fist(fist_cells[2]) if len(fist_cells) > 2 else None
                )

                # Odds
                odds_row = record_items[3] if len(record_items) > 3 else None
                f1_odds = f2_odds = None
                if odds_row:
                    odds_vals = odds_row.css(
                        "p.paragraph-6::text, p.paragraph-7::text"
                    ).getall()
                    if len(odds_vals) >= 2:
                        f1_odds, f2_odds = odds_vals[0].strip(), odds_vals[1].strip()

                bouts.append(
                    {
                        "event_slug": event_slug,
                        "card": card_name,
                        "bout_type": bout_type,
                        "division": division,
                        "fighter_1_corner": f1_corner,
                        "fighter_1_slug": slug(f1_headshot),
                        "fighter_1_uuid": f1_uuid,
                        "fighter_1_weight": f1_weight,
                        "fighter_1_height": f1_height,
                        "fighter_1_fist_size": f1_fist_size,
                        "fighter_1_odds": f1_odds,
                        "fighter_2_corner": f2_corner,
                        "fighter_2_slug": slug(f2_headshot),
                        "fighter_2_uuid": f2_uuid,
                        "fighter_2_weight": f2_weight,
                        "fighter_2_height": f2_height,
                        "fighter_2_fist_size": f2_fist_size,
                        "fighter_2_odds": f2_odds,
                    }
                )

        bouts.reverse()
        for i, bout in enumerate(bouts, start=1):
            item = BKFCBoutItem()
            item["order"] = i
            for key, value in bout.items():
                item[key] = value
            yield item
