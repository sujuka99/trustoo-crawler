from collections.abc import Iterator
from enum import StrEnum
from typing import Any

from scrapy import Request, Spider
from scrapy.http import HtmlResponse

from trustoo_crawler.items import BusinessItem, WorkingTimeItem
from trustoo_crawler.utils import WeekDays

BASE_URL = "https://www.goudengids.nl"
START_URL = "https://www.goudengids.nl/nl/bedrijven/advocaten/"
PAGE_URL = "https://www.goudengids.nl/nl/zoeken/advocaten/"
XPATH_CONTAINS = (
    "//{element}[contains(concat(' ', normalize-space({attr}), ' '), '{val}')]"
)


class GoudenGidsXPaths(StrEnum):
    """Stores useful xpaths."""

    NAME = XPATH_CONTAINS.format(element="h1", attr="@itemprop", val="name")
    LOCATION = XPATH_CONTAINS.format(element="span", attr="@itemprop", val="address")
    DESCRIPTION = f"{XPATH_CONTAINS.format(element="div", attr="h3/text()", val="Beschrijving")}/div"
    PHONE = XPATH_CONTAINS.format(element="a", attr="@data-ta", val="PhoneButtonClick")
    WEBSITE = f"{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="WebsiteActionClick")}/@data-js-value"
    EMAIL = f"{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="EmailActionClick")}/@data-js-value"
    SOCIAL_MEDIA = f"{XPATH_CONTAINS.format(element="div", attr="@class", val="flex flex-wrap social-media-wrap")}/a/@href"
    PAYMENT_OPTIONS = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Betaalmogelijkheden")}"
        f"//li/@title"
    )
    CERTIFICATES = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Certificeringen")}"
        "//li/span/text()"
    )
    OTHER_INFORMATION_SECTION = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Overige informatie")}"
        f"{XPATH_CONTAINS.format(element="div", attr="span/@class", val="tab__subtitle")}"
    )
    OTHER_INFORMATION_SECTION_TITLE = "normalize-space(span)"
    OTHER_INFORMATION_SECTION_VALUE = "//li/span/text()"
    WORKING_DAY = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Openingsuren")}"
        f"{XPATH_CONTAINS.format(element="div", attr="div/text()", val="{day}")}"
    )
    MAX_PAGE = "/html/body/main/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[8]/a/text()"  # TODO(Ivan Yordanov): Move away from absolute address
    LISTING = f"{XPATH_CONTAINS.format(element="li", attr="@itemtype", val="http://schema.org/LocalBusiness")}/@data-href"
    PARKING_INFO = (
        f"{XPATH_CONTAINS.format(element="div", attr="@id", val="parking-info")}//li"
    )
    PARKING_INFO_SECTION_NAME = "normalize-space(span)"
    PARKING_INFO_SECTION_VALUE = "text()"
    ECONOMIC_DATA = (
        f"{XPATH_CONTAINS.format(element="div", attr="@id", val="economic-data")}//li"
    )
    ECONOMIC_DATA_SECTION_NAME = "normalize-space(span)"
    ECONOMIC_DATA_SECTION_VALUE = "text()"


class GoudenGidsSpider(Spider):
    name = "gouden_gids"
    start_urls = [START_URL]

    def parse(self, response: HtmlResponse, **kwargs) -> Iterator[Request]:
        """Find the number of pages for a specific category, call `parse_page` on each."""
        max_page_xpath = GoudenGidsXPaths.MAX_PAGE
        max_page = int(response.xpath(max_page_xpath)[0].get())
        self.log(max_page)
        # for page_number in range(1, max_page + 1):  # TODO(Ivan Yordanov): Uncomment, parametrize
        for page_number in range(1, 2):
            page_url = f"{PAGE_URL}{page_number}/"
            self.log(page_url)
            yield Request(
                page_url,
                callback=self.parse_page,
                meta={"handle_httpstatus_list": [302]},
            )

    def parse_page(self, response: HtmlResponse) -> Iterator[Request]:
        """Find all businesses in a "search" page, call `parse_business_page` on each."""
        listings_path = GoudenGidsXPaths.LISTING
        listings_urls: list[str] = response.xpath(listings_path).getall()
        # for url in listings_urls:  # TODO(Ivan Yordanov): Uncomment
        for url in listings_urls:
            yield Request(BASE_URL + url, callback=self.parse_business_page)

    def parse_business_page(self, response: HtmlResponse) -> Iterator[BusinessItem]:
        """Yield item containing all scraped details bout a business."""
        self.log(response.url)
        self.log(response.status)
        business_item = BusinessItem(
            name=self.get_element_text(response, GoudenGidsXPaths.NAME),
            location=self.get_element_text(response, GoudenGidsXPaths.LOCATION),
            description=self.get_element_text(response, GoudenGidsXPaths.DESCRIPTION),
            phone=self.get_element_text(response, GoudenGidsXPaths.PHONE),
            website=self.get_element_text(response, GoudenGidsXPaths.WEBSITE),
            email=self.get_element_text(response, GoudenGidsXPaths.EMAIL),
            social_media=self.get_element_texts(
                response, GoudenGidsXPaths.SOCIAL_MEDIA
            ),
            payment_options=self.get_element_texts(
                response, GoudenGidsXPaths.PAYMENT_OPTIONS
            ),
            certificates=self.get_element_text(response, GoudenGidsXPaths.CERTIFICATES),
            other_information=self.get_other_information(
                response,
                GoudenGidsXPaths.OTHER_INFORMATION_SECTION,
                GoudenGidsXPaths.OTHER_INFORMATION_SECTION_TITLE,
                GoudenGidsXPaths.OTHER_INFORMATION_SECTION_VALUE,
            ),
            working_time=self.get_working_times(response),
            # TODO(Ivan Yordanov): Broken because the content is loaded dynamically
            # Try to get the data from seety.co/nl by using the available details
            # about location.
            parking_info=self.get_other_information(
                response,
                GoudenGidsXPaths.PARKING_INFO,
                GoudenGidsXPaths.PARKING_INFO_SECTION_NAME,
                GoudenGidsXPaths.PARKING_INFO_SECTION_VALUE,
            ),
            economic_data=self.get_other_information(
                response,
                GoudenGidsXPaths.ECONOMIC_DATA,
                GoudenGidsXPaths.ECONOMIC_DATA_SECTION_NAME,
                GoudenGidsXPaths.ECONOMIC_DATA_SECTION_VALUE,
            ),
        )
        yield business_item

    def get_element_text(self, response: HtmlResponse, xpath: str) -> str:
        return response.xpath(f"normalize-space({xpath})").get() or ""

    def get_element_texts(self, response: HtmlResponse, xpath: str) -> list[str]:
        return [el.strip() for el in response.xpath(xpath).getall()] or []

    def get_working_time_day(self, response: HtmlResponse, day: WeekDays) -> str:
        return (
            response.xpath(
                f"normalize-space({GoudenGidsXPaths.WORKING_DAY.format(day=day)})"
            ).get()
            or ""
        )

    def get_working_times(self, response: HtmlResponse) -> WorkingTimeItem:
        return WorkingTimeItem(
            monday=self.get_working_time_day(response, WeekDays.MONDAY),
            tuesday=self.get_working_time_day(response, WeekDays.TUESDAY),
            wednesday=self.get_working_time_day(response, WeekDays.WEDNESDAY),
            thursday=self.get_working_time_day(response, WeekDays.THURSDAY),
            friday=self.get_working_time_day(response, WeekDays.FRIDAY),
            saturday=self.get_working_time_day(response, WeekDays.SATURDAY),
            sunday=self.get_working_time_day(response, WeekDays.SUNDAY),
        )

    def get_other_information(
        self,
        response: HtmlResponse,
        sections_xpath: str,
        section_name_xpath: str,
        section_value_xpath: str,
    ) -> dict[str, Any]:
        sections = response.xpath(sections_xpath)
        return {
            section.xpath(section_name_xpath).get() or "": [
                el.strip() for el in section.xpath(section_value_xpath).getall()
            ]
            for section in sections
        }
