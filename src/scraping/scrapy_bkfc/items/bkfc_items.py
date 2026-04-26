# standard library imports

# third party imports
from scrapy import Field, Item

# local imports


class BKFCFighterItem(Item):
    slug = Field()
    name = Field()
    wins = Field()
    losses = Field()
    draws = Field()
    division = Field()
    reach = Field()
    height = Field()
    nickname = Field()
    dob = Field()
    nationality = Field()
    social_media = Field()


class BKFCEventItem(Item):
    slug = Field()
    name = Field()
    page = Field()
    page_position = Field()
    datetime_est = Field()
    venue = Field()
    live_stats_id = Field()
    final_stats_id = Field()


class BKFCBoutItem(Item):
    event_slug = Field()
    order = Field()
    card = Field()
    bout_type = Field()
    division = Field()
    fighter_1_corner = Field()
    fighter_1_slug = Field()
    fighter_1_uuid = Field()
    fighter_1_weight = Field()
    fighter_1_height = Field()
    fighter_1_fist_size = Field()
    fighter_1_odds = Field()
    fighter_2_corner = Field()
    fighter_2_slug = Field()
    fighter_2_uuid = Field()
    fighter_2_weight = Field()
    fighter_2_height = Field()
    fighter_2_fist_size = Field()
    fighter_2_odds = Field()
