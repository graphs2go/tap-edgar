from typing import List, Iterable

from singer_sdk import Tap

from tap_edgar.streams.tap_edgar_stream import TapEdgarStream

from singer_sdk.typing import (
    NumberType,
    PropertiesList,
    Property,
    StringType,
    ObjectType,
)


class Edgar10kStream(TapEdgarStream):
    schema = PropertiesList(
        Property("cik", NumberType),
        Property(
            "company",
            ObjectType(
                Property("cik", NumberType),
                Property("confirmed_name", StringType),
            ),
        ),
    )
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
