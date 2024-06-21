from pathlib import Path

import pytest

from tests.utils import read_response_from_file
from trustoo_crawler.spiders.gouden_gids_lawyers import GoudenGidsLawyersSpider


class TestGoudenGidsSpider:

    responses_path = "test_gouden_gids/responses"

    @pytest.fixture()
    def spider(self) -> GoudenGidsLawyersSpider:
        return GoudenGidsLawyersSpider()

    def test_parse(self, spider: GoudenGidsLawyersSpider):
        results = spider.parse(
            read_response_from_file(
                Path(f"{self.responses_path}/lawyers_search_p1.html"),
                "https://www.goudengids.nl/nl/bedrijven/advocaten/",
            )
        )
        assert next(iter(results)).url == "https://www.goudengids.nl/nl/zoeken/advocaten/1/"

    def test_parse_page(self, spider: GoudenGidsLawyersSpider):
        results = spider.parse_page(
            read_response_from_file(
                Path(f"{self.responses_path}/lawyers_search_p1.html"),
                "https://www.goudengids.nl/nl/zoeken/advocaten/1/"
            )
        )
        assert next(iter(results)).url == "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119701094/Rijnja+Meijer+%26+Balemans+Advocaten/"

    def test_parse_business_page(self, spider: GoudenGidsLawyersSpider):
        results = spider.parse_business_page(
            read_response_from_file(
                Path(f"{self.responses_path}/backer_and_mckenzie.html"),
                "https://www.goudengids.nl/nl/bedrijf/Amsterdam/L119193538/Baker+%26+McKenzie+Amsterdam+NV/"
            )
        )
        assert next(iter(results))["name"] == "Baker & McKenzie Amsterdam NV"
