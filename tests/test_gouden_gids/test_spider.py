from collections.abc import Iterator
from enum import Enum
from pathlib import Path

import pytest
from scrapy import Request

from tests.utils import read_response_from_file
from trustoo_crawler.spiders.gouden_gids_lawyers import (
    GoudenGidsLawyersSpider,
    GoudenGidsXPaths,
)

RESPONSES_PATH = "test_gouden_gids/responses"


class LawyerResponse(Enum):
    BAKER_AND_MCKENZIE = read_response_from_file(
        Path(f"{RESPONSES_PATH}/backer_and_mckenzie.html"),
        "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119193538/Baker+%26+McKenzie+Amsterdam+NV/",
    )
    HENDRICKS = read_response_from_file(
        Path(f"{RESPONSES_PATH}/hendricks_short_description.html"),
        "https://www.goudengids.nl/nl/bedrijf/Deurne/L145578951/Advocatenkantoor+Hendriks/",
    )


class TestGoudenGidsLawyersSpider:
    @pytest.fixture()
    def spider(self) -> GoudenGidsLawyersSpider:
        return GoudenGidsLawyersSpider()

    @pytest.fixture
    def front_page_requests(self, spider: GoudenGidsLawyersSpider) -> Iterator[Request]:
        return spider.parse(
            read_response_from_file(
                Path(f"{RESPONSES_PATH}/lawyers_search_p1.html"),
                "https://www.goudengids.nl/nl/bedrijven/advocaten/",
            )
        )

    @pytest.fixture
    def search_page_requests(
        self, spider: GoudenGidsLawyersSpider
    ) -> Iterator[Request]:
        return spider.parse_page(
            read_response_from_file(
                Path(f"{RESPONSES_PATH}/lawyers_search_p1.html"),
                "https://www.goudengids.nl/nl/bedrijven/advocaten/",
            )
        )

    def test_parse(self, front_page_requests: Iterator[Request]):
        assert (
            next(iter(front_page_requests)).url
            == "https://www.goudengids.nl/nl/zoeken/advocaten/1/"
        )

    def test_parse_page(self, search_page_requests: Iterator[Request]):
        assert (
            next(iter(search_page_requests)).url
            == "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119701094/Rijnja+Meijer+%26+Balemans+Advocaten/"
        )

    def test_parse_business_page(self, spider: GoudenGidsLawyersSpider):
        items = spider.parse_business_page(
            read_response_from_file(
                Path(f"{RESPONSES_PATH}/backer_and_mckenzie.html"),
                "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119193538/Baker+%26+McKenzie+Amsterdam+NV/",
            )
        )
        assert next(iter(items))["name"] == "Baker & McKenzie Amsterdam NV"

    @pytest.mark.parametrize(
        ("response", "xpath", "expected"),
        [
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE,
                f"normalize-space({GoudenGidsXPaths.NAME})",
                ["Baker & McKenzie Amsterdam NV"],
                id="name",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE,
                f"normalize-space({GoudenGidsXPaths.LOCATION})",
                ["Claude Debussylaan 54, 1082MD Amsterdam"],
                id="location",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS,
                f"normalize-space({GoudenGidsXPaths.DESCRIPTION})",
                ["kantoor gericht op rechtshulp aan on- of minvermogenden"],
                id="description",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS,
                f"normalize-space({GoudenGidsXPaths.PHONE})",
                ["+31493321872"],
                id="phone",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS,
                f"normalize-space({GoudenGidsXPaths.WEBSITE})",
                ["https://www.advocaathendriks.nl"],
                id="website",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE,
                f"normalize-space({GoudenGidsXPaths.EMAIL})",
                ["info.amsterdam@bakermckenzie.com"],
                id="email",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE,
                f"{GoudenGidsXPaths.SOCIAL_MEDIA}",
                [
                    "https://www.facebook.com/BakerMcKenzieAmsterdam/",
                    "https://twitter.com/BakerMcKenzieNL",
                    "https://www.instagram.com/bakermckenzie_amsterdam",
                    "https://www.linkedin.com/company/baker_mckenzie_amsterdam/",
                ],
                id="social",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS,
                f"normalize-space({GoudenGidsXPaths.WORKING_TIMES})",
                [
                    "Openingsuren Nu geopend - 9:00 - 17:30 Maandag 9:00 - 17:30 Dinsdag 9:00 - 17:30 Woensdag 9:00 - 17:30 Donderdag 9:00 - 17:30 Vrijdag 9:00 - 17:30"
                ],
                id="working-times",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS,
                f"{GoudenGidsXPaths.CERTIFICATES}",
                [
                    "Branche organisatie:VAJN",
                    "Gecertificeerd door:High Trust Raad voor Rechtsbijstand",
                    "Overig:.",
                ],
                id="certificates",
            ),
        ],
    )
    def test_xpath(self, response: LawyerResponse, xpath: str, expected: str):
        assert [el.strip() for el in response.value.xpath(xpath).getall()] == expected
