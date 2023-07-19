from __future__ import annotations

from datetime import date
from typing import List

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_edgar.streams.edgar_10k_stream import Edgar10kStream
from tap_edgar.streams.tap_edgar_stream import TapEdgarStream


class TapEdgar(Tap):
    """tap_edgar tap class."""

    name = "tap-edgar"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "companies",
            th.ArrayType(
                th.ObjectType(
                    th.Property("cik", th.StringType, required=True),
                )
            ),
        )
    ).to_dict()

    def discover_streams(self) -> List[TapEdgarStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            Edgar10kStream(self),
        ]


if __name__ == "__main__":
    TapEdgar.cli()
