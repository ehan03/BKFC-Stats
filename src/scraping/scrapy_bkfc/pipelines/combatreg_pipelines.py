# standard library imports
import json
import os

# third party imports

# local imports


class CombatRegistryMetaPipeline:
    def __init__(self):
        self.items = []

        self.dir_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "raw",
            "combatreg",
        )

    def process_item(self, item, spider):
        self.items.extend(item)

        return item

    def close_spider(self, spider):
        with open(
            os.path.join(self.dir_path, "metadata.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
