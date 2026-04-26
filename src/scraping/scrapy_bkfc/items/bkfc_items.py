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
