# standard library imports
import os

# third party imports
import pandas as pd

# local imports
from ..items.bkfc_items import BKFCBoutItem, BKFCEventItem, BKFCFighterItem


class BKFCFighterPipeline:
    def __init__(self):
        self.fighters = []
        self.fighters_df_cols = [
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
        fighters_df = fighters_df[self.fighters_df_cols]

        fighters_df.to_csv(os.path.join(self.dir_path, "fighters.csv"), index=False)


class BKFCEventPipeline:
    def __init__(self):
        self.events = []
        self.bouts = []
        self.events_df_cols = [
            "slug",
            "name",
            "page",
            "page_position",
            "datetime_est",
            "venue",
            "live_stats_id",
            "final_stats_id",
        ]
        self.bouts_df_cols = [
            "event_slug",
            "order",
            "card",
            "bout_type",
            "division",
            "fighter_1_corner",
            "fighter_1_slug",
            "fighter_1_uuid",
            "fighter_1_weight",
            "fighter_1_height",
            "fighter_1_fist_size",
            "fighter_1_odds",
            "fighter_2_corner",
            "fighter_2_slug",
            "fighter_2_uuid",
            "fighter_2_weight",
            "fighter_2_height",
            "fighter_2_fist_size",
            "fighter_2_odds",
        ]

        self.dir_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "bkfc"
        )

    def process_item(self, item, spider):
        if isinstance(item, BKFCEventItem):
            self.events.append(dict(item))
        elif isinstance(item, BKFCBoutItem):
            self.bouts.append(dict(item))

        return item

    def close_spider(self, spider):
        events_df = (
            pd.DataFrame(self.events)
            .sort_values(by=["page", "page_position"], ascending=[False, False])
            .reset_index(drop=True)
        )
        event_slugs = events_df["slug"].values.tolist()

        bouts_df = (
            pd.DataFrame(self.bouts)
            .sort_values(
                by=["event_slug", "order"],
                key=lambda x: (
                    x
                    if x.name != "event_slug"
                    else x.map(lambda e: event_slugs.index(e))  # type: ignore
                ),
            )
            .reset_index(drop=True)
        )

        events_df = events_df[self.events_df_cols]
        bouts_df = bouts_df[self.bouts_df_cols]

        events_df.to_csv(os.path.join(self.dir_path, "events.csv"), index=False)
        bouts_df.to_csv(os.path.join(self.dir_path, "bouts.csv"), index=False)
