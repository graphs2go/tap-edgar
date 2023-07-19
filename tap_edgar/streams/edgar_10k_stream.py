import re
from typing import Dict, Any

from tap_edgar.streams.tap_edgar_stream import TapEdgarStream
import singer_sdk.typing as th


class Edgar10kStream(TapEdgarStream):
    filing_properties = (th.Property("item_1a", th.StringType),)
    filing_type = "10-K"
    name = "edgar-10-k"

    def _parse_filing_html(self, *, filing_html: str) -> Dict[str, Any]:
        return {"item_1a": self.__parse_item_1a(filing_html=filing_html)}

    def __parse_item_1a(self, *, filing_html: str):
        # Adapted from https://github.com/sheth7/SEC-risks
        data = filing_html.lower()

        #    removing the html tags from data
        clean = re.compile(r"<(.|\s)*?>")
        new_data = re.sub(clean, " ", data)

        new_data = new_data.replace("&#8217;", "'").replace("&#39;", "'")

        #    removing the &#; from data
        clean = re.compile(r"&#.*?;")
        new_data = re.sub(clean, " ", new_data)

        #    removing the &nbsp; from data
        clean = re.compile(r"&nbsp;")
        new_data = re.sub(clean, " ", new_data)

        #    keeping the string between the two Item 1A. and Item 1B.
        data1 = re.findall(r"item 1a\.(.+?)item 1b\.", new_data, re.S)
        new_data1 = " ".join(data1)

        #    keeping the string between the two Item 7. and Item 8.
        data2 = re.findall(r"item 7a\.(.+?)item 8\.", new_data, re.S)
        new_data2 = " ".join(data2)

        new_data = new_data1 + new_data2

        #    removing the \ss\s from data
        clean = re.compile(r"\ss\s")
        new_data = re.sub(clean, " ", new_data)

        return " ".join(new_data.strip().split())
