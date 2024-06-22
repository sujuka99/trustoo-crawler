from collections.abc import Iterator
from enum import Enum
from pathlib import Path

import pytest
from scrapy import Request
from scrapy.http import HtmlResponse

from tests.utils import read_response_from_file
from trustoo_crawler.spiders.gouden_gids import (
    GoudenGidsSpider,
    GoudenGidsXPaths,
)
from trustoo_crawler.utils import WeekDays

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
    BREEWEL = read_response_from_file(
        Path(f"{RESPONSES_PATH}/breewel_payment_options.html"),
        "https://www.goudengids.nl/nl/bedrijf/Bergen+op+Zoom/L146093845/Breewel+Advocatuur/",
    )


class TestGoudenGidsSpider:
    @pytest.fixture()
    def spider(self) -> GoudenGidsSpider:
        return GoudenGidsSpider()

    @pytest.fixture
    def front_page_requests(self, spider: GoudenGidsSpider) -> Iterator[Request]:
        return spider.parse(
            read_response_from_file(
                Path(f"{RESPONSES_PATH}/lawyers_search_p1.html"),
                "https://www.goudengids.nl/nl/bedrijven/advocaten/",
            )
        )

    @pytest.fixture
    def search_page_requests(self, spider: GoudenGidsSpider) -> Iterator[Request]:
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

    def test_parse_business_page(self, spider: GoudenGidsSpider):
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
                LawyerResponse.BAKER_AND_MCKENZIE.value,
                f"normalize-space({GoudenGidsXPaths.NAME})",
                ["Baker & McKenzie Amsterdam NV"],
                id="name",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value,
                f"normalize-space({GoudenGidsXPaths.LOCATION})",
                ["Claude Debussylaan 54, 1082MD Amsterdam"],
                id="location",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS.value,
                f"normalize-space({GoudenGidsXPaths.DESCRIPTION})",
                ["kantoor gericht op rechtshulp aan on- of minvermogenden"],
                id="description",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS.value,
                f"normalize-space({GoudenGidsXPaths.PHONE})",
                ["+31493321872"],
                id="phone",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS.value,
                f"normalize-space({GoudenGidsXPaths.WEBSITE})",
                ["https://www.advocaathendriks.nl"],
                id="website",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value,
                f"normalize-space({GoudenGidsXPaths.EMAIL})",
                ["info.amsterdam@bakermckenzie.com"],
                id="email",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value,
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
                LawyerResponse.HENDRICKS.value,
                f"normalize-space({GoudenGidsXPaths.WORKING_DAY.format(day=WeekDays.MONDAY)})",
                ["Maandag 9:00 - 17:30"],
                id="working-times",
            ),
            pytest.param(
                LawyerResponse.HENDRICKS.value,
                f"{GoudenGidsXPaths.CERTIFICATES}",
                [
                    "Branche organisatie:VAJN",
                    "Gecertificeerd door:High Trust Raad voor Rechtsbijstand",
                    "Overig:.",
                ],
                id="certificates",
            ),
            pytest.param(
                LawyerResponse.BREEWEL.value,
                f"{GoudenGidsXPaths.PAYMENT_OPTIONS}",
                [
                    "Bank / giro",
                    "Contant",
                    "Factuur",
                ],
                id="payment-options",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value,
                f"{GoudenGidsXPaths.PARKING_INFO}",
                [
                    '<li class="block mb-2 flex justify-between"><span class="font-semibold">Soort parking:</span> Voetgangerszone</li>',
                    '<li class="block mb-2 flex justify-between"><span class="font-semibold">Uren:</span> 0:00-24:00</li>',
                ],
                id="parking-info",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value.xpath(
                    GoudenGidsXPaths.PARKING_INFO
                ),
                f"{GoudenGidsXPaths.PARKING_INFO_SECTION_NAME}",
                ["Soort parking:", "Uren:"],
                id="parking-info-section-name",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value.xpath(
                    GoudenGidsXPaths.PARKING_INFO
                ),
                f"{GoudenGidsXPaths.PARKING_INFO_SECTION_VALUE}",
                ["Voetgangerszone", "0:00-24:00"],
                id="parking-info-section-value",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value,
                f"{GoudenGidsXPaths.ECONOMIC_DATA}",
                [
                    '<li class="block mb-2 flex justify-between"><span '
                    'class="font-semibold">KVK-nummer:</span> 34276539</li>',
                    '<li class="block mb-2 flex justify-between"><span '
                    'class="font-semibold">Oprichtingsdatum:</span> 18/6/2007</li>',
                    '<li class="block mb-2 flex justify-between"><span '
                    'class="font-semibold">Aantal werknemers:</span> 1</li>',
                    '<li class="block mb-2 flex justify-between"><span '
                    'class="font-semibold">Status:</span> Actief</li>',
                ],
                id="economic-data",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value.xpath(
                    GoudenGidsXPaths.ECONOMIC_DATA
                ),
                f"{GoudenGidsXPaths.ECONOMIC_DATA_SECTION_NAME}",
                [
                    "KVK-nummer:",
                    "Oprichtingsdatum:",
                    "Aantal werknemers:",
                    "Status:",
                ],
                id="economic-data-section-name",
            ),
            pytest.param(
                LawyerResponse.BAKER_AND_MCKENZIE.value.xpath(
                    GoudenGidsXPaths.ECONOMIC_DATA
                ),
                f"{GoudenGidsXPaths.ECONOMIC_DATA_SECTION_VALUE}",
                [
                    "34276539",
                    "18/6/2007",
                    "1",
                    "Actief",
                ],
                id="economic-data-section-value",
            ),
        ],
    )
    def test_xpath(self, response: HtmlResponse, xpath: str, expected: str):
        assert [el.strip() for el in response.xpath(xpath).getall()] == expected

    def test_get_other_information(self, spider: GoudenGidsSpider):
        parking_info = spider.get_other_information(
            read_response_from_file(
                Path(f"{RESPONSES_PATH}/backer_and_mckenzie.html"),
                "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119193538/Baker+%26+McKenzie+Amsterdam+NV/",
            ),
            GoudenGidsXPaths.PARKING_INFO,
            GoudenGidsXPaths.PARKING_INFO_SECTION_NAME,
            GoudenGidsXPaths.PARKING_INFO_SECTION_VALUE,
        )
        assert parking_info == {
            "Soort parking:": ["Voetgangerszone"],
            "Uren:": ["0:00-24:00"],
        }
