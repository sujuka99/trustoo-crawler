from collections.abc import Iterator
from enum import StrEnum

from scrapy import Request, Spider
from scrapy.http import HtmlResponse

from trustoo_crawler.items import BusinessItem, WorkingTimeItem

BASE_URL = "https://www.goudengids.nl"
START_URL = "https://www.goudengids.nl/nl/bedrijven/advocaten/"
PAGE_URL = "https://www.goudengids.nl/nl/zoeken/advocaten/"
WEEKDAYS = (
    "Maandag",
    "Dinsdag",
    "Woensdag",
    "Donderdag",
    "Vrijdag",
    "Zaterdag",
    "Zondag",
)
XPATH_CONTAINS = (
    "//{element}[contains(concat(' ', normalize-space({attr}), ' '), '{val}')]"
)
XPATH_IF = (
    "concat("
    "   substring({true}, 1, number({condition}) * string-length({true}))"
    "   substring({false}, 1, number(not({condition})) * string-length({false}))"
    ")"
)


class WeekDays(StrEnum):
    MONDAY = "Maandag"
    TUESDAY = "Dinsdag"
    WEDNESDAY = "Woensdag"
    THURSDAY = "Donderdag"
    FRIDAY = "Vrijdag"
    SATURDAY = "Zaterdag"
    SUNDAY = "Zondag"


class GoudenGidsXPaths(StrEnum):
    NAME = XPATH_CONTAINS.format(element="h1", attr="@itemprop", val="name")
    LOCATION = XPATH_CONTAINS.format(element="span", attr="@itemprop", val="address")
    DESCRIPTION = f"{XPATH_CONTAINS.format(element="div", attr="h3/text()", val="Beschrijving")}/div"
    PHONE = XPATH_CONTAINS.format(element="a", attr="@data-ta", val="PhoneButtonClick")
    WEBSITE = f"{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="WebsiteActionClick")}/@data-js-value"
    EMAIL = f"{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="EmailActionClick")}/@data-js-value"
    SOCIAL_MEDIA = f"{XPATH_CONTAINS.format(element="div", attr="@class", val="flex flex-wrap social-media-wrap")}/a/@href"
    HOURLY_RATE = "/html/body/main/div[3]/div/div/div[3]/div/div/div[3]/div/div[13]/ul/li/span"  # TODO
    PAYMENT_OPTIONS = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Betaalmogelijkheden")}"
        f"//li/@title"
    )
    CERTIFICATES = (
        f"{XPATH_CONTAINS.format(element="div", attr="h3", val="Certificeringen")}"
        "//li/span/text()"
    )
    OTHER_INFORMATION = "/html/body/main/div[3]/div/div/div[3]/div/div/div[3]/div"  # TODO(Ivan Yordanov): Break down into more useful info
    WORKING_TIMES = XPATH_CONTAINS.format(
        element="div", attr="./h3", val="Openingsuren"
    )
    WORKING_DAY = (
        f"{XPATH_CONTAINS.format(element="div", attr="./h3", val="Openingsuren")}"
        f"{XPATH_CONTAINS.format(element="div", attr="div/text()", val="{day}")}"
    )
    WORKING_TIME_AM = (
        f"{XPATH_CONTAINS.format(element="div", attr="./h3", val="Openingsuren")}"
        f"{XPATH_CONTAINS.format(element="div", attr="div/text()", val="{day}")}"
        f"{XPATH_CONTAINS.format(element="div", attr="@class", val="oh-table__am whitespace-nowrap mr-1 md:mr-3")}"
    )
    WORKING_TIME_PM = (
        f"{XPATH_CONTAINS.format(element="div", attr="./h3", val="Openingsuren")}"
        f"{XPATH_CONTAINS.format(element="div", attr="div/text()", val="{day}")}"
        f"{XPATH_CONTAINS.format(element="div", attr="@class", val="oh-table__pm whitespace-nowrap")}"
    )


class GoudenGidsLawyersSpider(Spider):
    name = "gouden_gids"
    start_urls = [START_URL]

    def parse(self, response: HtmlResponse, **kwargs) -> Iterator[Request]:
        """Find the number of pages for a specific category, call `parse_page` on each."""
        max_page_xpath = (
            "/html/body/main/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[8]/a/text()"
        )
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
        listings_path = (
            "/html/body/main/div/div/div[2]/div[1]/div[2]/div[1]/ol/li/@data-href"
        )
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
            # hourly_rate=self.get_element_text(response, GoudenGidsXPaths.HOURLY_RATE),
            payment_options=self.get_element_texts(
                response, GoudenGidsXPaths.PAYMENT_OPTIONS
            ),
            certificates=self.get_element_text(response, GoudenGidsXPaths.CERTIFICATES),
            # other_information=self.get_element_text(response, GoudenGidsXPaths.OTHER_INFORMATION),
            working_time=self.get_working_times(response),
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
