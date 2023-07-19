"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_edgar.tap import TapEdgar

SAMPLE_CONFIG = {
    "companies": [
        {"cik": "0000066740"},
    ]
}


# Run standard built-in tap tests from the SDK:
TestTapEdgar = get_tap_test_class(
    tap_class=TapEdgar,
    config=SAMPLE_CONFIG,
)
