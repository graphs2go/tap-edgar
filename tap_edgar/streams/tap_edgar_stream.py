import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Tuple, Dict, Any
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup, Tag
from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterSession, LimiterMixin
from singer_sdk import Stream, Tap
import singer_sdk.typing as th


class _CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """Session class with caching and rate-limiting behavior. Accepts arguments for both
    LimiterSession and CachedSession.
    """


class TapEdgarStream(Stream, ABC):
    filing_type: str
    schema = th.PropertiesList(
        th.Property("cik", th.StringType),
        th.Property(
            "company",
            th.ObjectType(th.Property("cik", th.StringType)),
        ),
        th.Property("filing", th.ObjectType(th.Property("type", th.StringType))),
    ).to_dict()
    identifier = ["cik"]

    @dataclass(frozen=True)
    class _EntityRss:
        @dataclass(frozen=True)
        class CompanyInfo:
            cik: str
            confirmed_name: str

        @dataclass(frozen=True)
        class Filing:
            accession_number: str
            type: str

        company_info: CompanyInfo
        filings: Tuple[Filing, ...]

    def __init__(self, tap: Tap):
        super().__init__(tap=tap, name=None, schema=None)
        self.__requests_session = _CachedLimiterSession(
            ".http_cache", backend="filesystem", per_second=10
        )
        self.__request_headers = {"User-Agent": "Minor Gordon mail@minorgordon.net"}

    def __get_company_rss(self, company_cik: str) -> _EntityRss:
        response: requests.Response = self.__requests_session.get(
            "https://data.sec.gov/rss",
            headers=self.__request_headers,
            params={
                "cik": company_cik.lstrip("0"),
                "type": self.filing_type,
                "count": 40,
            },
        )
        response.raise_for_status()
        # see Gotchas, stripping whitespace and comments is highly recommended
        soup = BeautifulSoup(response.text, "xml")

        company_info_tag = soup.find("company-info")
        company_info = TapEdgarStream._EntityRss.CompanyInfo(
            cik=company_cik, confirmed_name=company_info_tag.find("confirmed-name").text
        )

        filings: List[TapEdgarStream._EntityRss.Filing] = []
        for entry_tag in soup.find_all("entry"):
            content_type_tag = entry_tag.find("content-type")
            filings.append(
                TapEdgarStream._EntityRss.Filing(
                    accession_number=content_type_tag.find("accession-number").text,
                    type=self.filing_type,
                )
            )

        return TapEdgarStream._EntityRss(
            company_info=company_info, filings=tuple(filings)
        )

    def __get_filing_html(self, accession_number: str, company_cik: str) -> str:
        base_url = f"https://www.sec.gov/Archives/edgar/data/{company_cik}/{accession_number.replace('-', '')}/"
        meta_links_json_response: requests.Response = self.__requests_session.get(
            base_url + "MetaLinks.json",
            headers=self.__request_headers,
        )
        meta_links_json_response.raise_for_status()
        meta_links_json = meta_links_json_response.json()
        meta_links_instance = meta_links_json["instance"]
        assert len(meta_links_instance) == 1
        html_file_name = tuple(meta_links_json["instance"].keys())[0]

        html_response: requests.Response = self.__requests_session.get(
            base_url + html_file_name, headers=self.__request_headers
        )
        html_response.raise_for_status()
        return html_response.text

    def get_records(self, company_config: dict) -> Iterable[dict]:
        company_rss = self.__get_company_rss(company_cik=company_config["cik"])
        for filing in company_rss.filings:
            record = {
                "company": dataclasses.asdict(company_rss.company_info),
                "filing": dataclasses.asdict(filing),
            }
            record.update(
                self._parse_filing_html(
                    filing_html=self.__get_filing_html(
                        accession_number=filing.accession_number,
                        company_cik=company_config["cik"],
                    )
                )
            )
            yield record

    @abstractmethod
    def _parse_filing_html(self, *, filing_html: str) -> Dict[str, Any]:
        raise NotImplementedError

    @property
    def partitions(self) -> List[dict]:
        return self.config.get("companies", [])
