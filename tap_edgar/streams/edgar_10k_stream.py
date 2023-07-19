from typing import Dict, Any

from tap_edgar.streams.tap_edgar_stream import TapEdgarStream


class Edgar10kStream(TapEdgarStream):
    filing_type = "10-K"
    name = "edgar-10-k"

    def _parse_filing_html(self, *, filing_html: str) -> Dict[str, Any]:
        return {}
