# standard library imports
import os

# third party imports
import pandas as pd

# local imports
from ..items.bkfc_items import BKFCFighterItem


class BKFCFighterPipeline:
    def __init__(self):
        self.fighters = []
        self.fighter_df_cols = [
            "slug",
            "name",
            "wins",
            "losses",
            "draws",
            "division",
            "reach",
            "height",
            "nickname",
            "dob",
            "nationality",
            "social_media",
        ]

        self.dir_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "bkfc"
        )

    def process_item(self, item, spider):
        if isinstance(item, BKFCFighterItem):
            self.fighters.append(dict(item))

        return item

    def close_spider(self, spider):
        fighters_df = (
            pd.DataFrame(self.fighters).sort_values(by="slug").reset_index(drop=True)
        )
        fighters_df = fighters_df[self.fighter_df_cols]

        fighters_df.to_csv(os.path.join(self.dir_path, "fighters.csv"), index=False)
