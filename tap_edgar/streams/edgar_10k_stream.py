from typing import List, Iterable

from singer_sdk import Tap

from tap_edgar.streams.tap_edgar_stream import TapEdgarStream

import singer_sdk.typing as th


class Edgar10kStream(TapEdgarStream):
    name = "edgar-10k"
    schema = th.PropertiesList(
        th.Property("cik", th.StringType),
        th.Property(
            "company",
            th.ObjectType(
                th.Property("cik", th.StringType),
                th.Property("confirmed_name", th.StringType),
            ),
        ),
    ).to_dict()
    identifier = ["cik"]

    def __init__(self, tap: Tap):
        super().__init__(tap=tap, name=None, schema=None)

    @property
    def partitions(self) -> List[dict]:
        return self.config.get("companies", [])

    def get_records(self, partition: dict) -> Iterable[dict]:
        return []
        # identifier = partition["identifier"]
        # name = partition.get("name")
        # amount = partition.get("amount", 1)
        #
        # price_data = Symbol(identifier).price_latest()
        #
        # decimal.getcontext().prec = 10
        # price = decimal.Decimal(str(price_data.price)) * decimal.Decimal(amount)
        #
        # record = {}
        # record["identifier"] = identifier
        # if name:
        #     record["name"] = name
        # record["price"] = price
        # record["currency"] = price_data.currency
        #
        # yield record
