from collections.abc import Iterator
from enum import StrEnum

from scrapy import Request, Spider
from scrapy.http import HtmlResponse

from trustoo_crawler.items import BusinessItem

BASE_URL = "https://www.goudengids.nl"
START_URL = "https://www.goudengids.nl/nl/bedrijven/advocaten/"
PAGE_URL = "https://www.goudengids.nl/nl/zoeken/advocaten/"

class GoudenGidsXPaths(StrEnum):
        NAME = "//h1[contains(concat(' ', normalize-space(@itemprop), ' '), 'name')]"
        LOCATION = "//span[contains(concat(' ', normalize-space(@itemprop), ' '), 'address')]"
        DESCRIPTION = "/html/body/main/div[3]/div/div/div[1]/div[4]"  # TODO
        PHONE = "//a[contains(concat(' ', normalize-space(@data-ta), ' '), 'PhoneButtonClick')]"
        WEBSITE = "//div[contains(concat(' ', normalize-space(@data-ta), ' '), 'WebsiteActionClick')]/@data-js-value"
        EMAIL = "//div[contains(concat(' ', normalize-space(@data-ta), ' '), 'EmailActionClick')]/@data-js-value"
        SOCIAL_MEDIA = "//div[contains(concat(' ', normalize-space(@class), ' '), 'flex flex-wrap social-media-wrap')]/@href"
        HOURLY_RATE = "/html/body/main/div[3]/div/div/div[3]/div/div/div[3]/div/div[13]/ul/li/span"  # TODO
        PAYMENT_OPTIONS = "/html/body/main/div[3]/div/div/div[3]/div/div/div[5]/div"  # TODO
        CERTIFICATES = "/html/body/main/div[3]/div/div/div[3]/div/div/div[4]/div/ul"  # TODO
        OTHER_INFORMATION = "/html/body/main/div[3]/div/div/div[3]/div/div/div[3]/div"  # TODO(Ivan Yordanov): Break down into more useful info
        WORKING_TIME = "//div[contains(concat(' ', normalize-space(@class), ' '), 'flex mb-2.5 opening-hours')]"

class GoudenGidsLawyersSpider(Spider):

    name = "gouden_gids"
    start_urls = [START_URL]

    def parse(self, response: HtmlResponse, **kwargs) -> Iterator[Request]:
        """Find the number of pages for a specific category, call `parse_page` on each."""
        max_page_xpath = "/html/body/main/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[8]/a/text()"
        max_page = int(response.xpath(max_page_xpath)[0].get())
        self.log(max_page)
        # for page_number in range(1, max_page + 1):  # TODO(Ivan Yordanov): Uncomment, parametrize
        for page_number in range(1, 3):
            page_url = f"{PAGE_URL}{page_number}/"
            self.log(page_url)
            yield Request(page_url, callback=self.parse_page, meta={"handle_httpstatus_list": [302]})

    def parse_page(self, response: HtmlResponse) -> Iterator[Request]:
        """Find all businesses in a "search" page, call `parse_business_page` on each."""
        listings_path = "/html/body/main/div/div/div[2]/div[1]/div[2]/div[1]/ol/li/@data-href"
        listings_urls: list[str] = response.xpath(listings_path).getall()
        # for url in listings_urls:  # TODO(Ivan Yordanov): Uncomment
        for url in listings_urls[0:2]:
            yield Request(BASE_URL + url, callback=self.parse_business_page)

    def parse_business_page(self, response: HtmlResponse) -> Iterator[BusinessItem]:
        """Yield item containing all scraped details bout a business"""
        self.log(response.url)
        self.log(response.status)
        business_item = BusinessItem(
            name=self.get_element_text(response, GoudenGidsXPaths.NAME),
            location=self.get_element_text_concat_list(response, GoudenGidsXPaths.LOCATION),
            # description=self.get_element_text(response, GoudenGidsXPaths.DESCRIPTION),
            phone=self.get_element_text_concat_list(response, GoudenGidsXPaths.PHONE),
            website=self.get_element_text(response, GoudenGidsXPaths.WEBSITE),
            email=self.get_element_text(response, GoudenGidsXPaths.EMAIL),
            social_media=self.get_element_text(response, GoudenGidsXPaths.SOCIAL_MEDIA),
            # hourly_rate=self.get_element_text(response, GoudenGidsXPaths.HOURLY_RATE),
            # payment_options=self.get_element_text(response, GoudenGidsXPaths.PAYMENT_OPTIONS),
            # certificates=self.get_element_text(response, GoudenGidsXPaths.CERTIFICATES),
            # other_information=self.get_element_text(response, GoudenGidsXPaths.OTHER_INFORMATION),
            working_time=self.get_element_text(response, GoudenGidsXPaths.WORKING_TIME),
        )
        yield business_item

    def get_element_text(self, response: HtmlResponse, xpath: str) -> str:
        return response.xpath(f"normalize-space({xpath})").get() or ""

    def get_element_text_concat_list(self, response: HtmlResponse, xpath: str) -> str:
        return " ".join(response.xpath(f"normalize-space({xpath})").getall()) or ""

