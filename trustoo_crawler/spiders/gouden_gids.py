from collections.abc import Iterator
from enum import StrEnum
from typing import Any

from scrapy import Request, Spider
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest

from trustoo_crawler.items import BusinessItem, WorkingTimeItem
from trustoo_crawler.utils import DutchWeekDay

# Store some usefule URLs in constants
BASE_URL = "https://www.goudengids.nl"  # The base of the later generated urls
# The URLs below are parametrized to allow the spider to crawl any category in Gouden gids
# Fortunately all categories share the same structure
START_URL = "https://www.goudengids.nl/nl/bedrijven/{category}/"  # The "starting" page for each category
PAGE_URL = "https://www.goudengids.nl/nl/zoeken/{category}/"  # The url shared by all pages of results for categories
# I have (over)used the construction below, so it made sense to parametrize it and
# store it in a constant
# As of writing this comment, I have no more time left to change things up and
# I just found out that this XPath does exactly do what I thought it did.
# This StackOverflow answer explains what happened:
# https://stackoverflow.com/a/46516155/11610149
XPATH_CONTAINS = (  # Find element that has a certain attribute of specific value
    "{element}[contains(concat(' ', normalize-space({attr}), ' '), '{val}')]"
)
# The task called for lawyers, so they are the default category
DEFAULT_CATEGORY = "advocaten"


class GoudenGidsXPaths(StrEnum):
    """Stores useful XPaths."""

    # I have not described all elements below as some are trivial to deduce from their names
    NAME = f"//{XPATH_CONTAINS.format(element="h1", attr="@itemprop", val="name")}"  # The name of the business
    LOCATION = (  # The address of the business
        f"//{XPATH_CONTAINS.format(element="span", attr="@itemprop", val="address")}"
    )
    DESCRIPTION = f"//{XPATH_CONTAINS.format(element="div", attr="h3/text()", val="Beschrijving")}/div"
    PHONE = f"//{XPATH_CONTAINS.format(element="a", attr="@data-ta", val="PhoneButtonClick")}"
    WEBSITE = f"//{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="WebsiteActionClick")}/@data-js-value"
    EMAIL = f"//{XPATH_CONTAINS.format(element="div", attr="@data-ta", val="EmailActionClick")}/@data-js-value"
    # All links towards social media
    SOCIAL_MEDIA = f"//{XPATH_CONTAINS.format(element="div", attr="@class", val="flex flex-wrap social-media-wrap")}/a/@href"
    PAYMENT_OPTIONS = (
        f"//{XPATH_CONTAINS.format(element="div", attr="h3", val="Betaalmogelijkheden")}"
        f"//li/@title"
    )
    CERTIFICATES = (
        f"//{XPATH_CONTAINS.format(element="div", attr="h3", val="Certificeringen")}"
        "//li/span/text()"
    )
    # Overige informatie
    OTHER_INFORMATION_SECTION = (
        f"//{XPATH_CONTAINS.format(element="div", attr="h3", val="Overige informatie")}"
        f"//{XPATH_CONTAINS.format(element="div", attr="span/@class", val="tab__subtitle")}"
    )
    # The name of a subsection in Overige informatie, to be used on the data that
    # `OTHER_INFORMATION_SECTION` has produced
    OTHER_INFORMATION_SECTION_TITLE = "normalize-space(span)"
    # The contents of a subsection in Overige informatie, to be used on the data that
    # `OTHER_INFORMATION_SECTION` has produced
    OTHER_INFORMATION_SECTION_VALUE = "//li/span/text()"
    # Parametrized, points towards a specific day in the Openingsuren section
    WORKING_DAY = (
        f"//{XPATH_CONTAINS.format(element="div", attr="h3", val="Openingsuren")}"
        f"//{XPATH_CONTAINS.format(element="div", attr="div/text()", val="{day}")}"
    )
    # Find the number of pages of results
    # TODO(Ivan Yordanov): Move away from absolute address
    MAX_PAGE = "/html/body/main/div/div/div[2]/div[1]/div[2]/div[2]/ul/li[8]/a/text()"
    LISTING = f"//{XPATH_CONTAINS.format(element="li", attr="@itemtype", val="http://schema.org/LocalBusiness")}/@data-href"
    # The folowing 3 XPaths work great on the HTML responses I downloaded for unit testing,
    # but since the parking info is generated dynamically using JS and seety.nl, scrapy
    # fails to return the actual values and instead returns meaningless parameter names.
    # Goes to show that unit testing must be accompanied by integration testing...
    # The element that contains the specifics about parking spaces
    PARKING_INFO = (
        f"//{XPATH_CONTAINS.format(element="div", attr="@id", val="parking-info")}//li"
    )
    # The name of a parking-related piece of information, to be used on the data that
    # `PARKING_INFO` has produced
    PARKING_INFO_SECTION_NAME = "normalize-space(span)"
    # The value of a parking-related piece of information, to be used on the data that
    # `PARKING_INFO` has produced
    PARKING_INFO_SECTION_VALUE = "text()"
    # The element that contains the specifics about financial data
    ECONOMIC_DATA = (
        f"//{XPATH_CONTAINS.format(element="div", attr="@id", val="economic-data")}//li"
    )
    # The name of a finance-related piece of information, to be used on the data that
    # `ECONOMIC_DATA` has produced
    ECONOMIC_DATA_SECTION_NAME = "normalize-space(span)"
    # The value of a finance-related piece of information, to be used on the data that
    # `ECONOMIC_DATA` has produced
    ECONOMIC_DATA_SECTION_VALUE = "text()"
    # Gets the link of the image used as logo for the business
    LOGO_SRC = (
        f"//{XPATH_CONTAINS.format(element="img", attr="@data-yext", val="logo")}/@src"
    )
    # Gets the link of the images stored in the gallery of the business
    PHOTO_SRC = (
        f"//{XPATH_CONTAINS.format(element="div", attr="@class", val="gallery flex flex-wrap")}"
        f"//{XPATH_CONTAINS.format(element="img", attr="@class", val="gallery__item")}"
        "/@src"
    )


class GoudenGidsSpider(Spider):
    """Spider that scrapes information from goudengids.nl.

    :param category: Category to scrape.
    :param max_page: Number of pages to scrape starting from page 1.
    """

    name = "gouden_gids"  # Name of the spider, seemed fitting to name it after the website

    # Overriding the object initialization to add parameters.
    # This way the user can provide as arguments the desired category
    # and the number of pages to scrape. I could allow selection of multiple categories at once,
    # but then the number of pages to scrape must be defined per category, so I
    # ultimately decided it was not worth the hassle for now.
    # I would make the crawler configurable via a YAML or maybe env vars to
    # enable more complicated scrapes with just 1 command.
    # For now if one wants to scrape more than 1 category with 1 command,
    # the easiest way is probably to write a simple parametrized bash function that
    # runs a couple instances of this spider.
    def __init__(
        self,
        name: str | None = None,
        category: str = DEFAULT_CATEGORY,
        max_page: str | None = None,
        **kwargs,
    ):
        self.category = category
        self.max_page = max_page
        super().__init__(name, **kwargs)

    def start_requests(self) -> Iterator[Request]:
        """Generate starting point(s) for the spider."""
        # Here is where the selected category is injected into the url that
        # determines the number of pages. The URL is then passed on to `self.parse`
        yield Request(START_URL.format(category=self.category), self.parse)

    def parse(self, response: HtmlResponse, **kwargs) -> Iterator[Request]:
        """Find the number of pages for a specific category, call `parse_page` on each."""
        # The max page to reach while crawling is either the one passed by the user (`self.max_page`)
        # or if the user didn't pass it, it is scraped from the category "home page"
        # That is also the only use of the category home page.
        # We have to scrape it though, because otherwise we couldn't detect whether
        # the user has passed a larger number of pages than exist.
        max_page = int(response.xpath(GoudenGidsXPaths.MAX_PAGE)[0].get())
        if self.max_page:
            # We could log here and notify the user if he provides too big of a number.
            max_page = min(int(self.max_page), max_page)
        for page_number in range(1, max_page + 1):
            # The search results share the same url, just with a different page number
            # at the end, hence we can generate all of those and call `parse_page` on
            # each.
            page_url = f"{PAGE_URL.format(category=self.category)}{page_number}/"
            yield Request(
                page_url,
                callback=self.parse_page,
            )

    # This is the function that generates the responses that we really care about
    def parse_page(self, response: HtmlResponse) -> Iterator[Request]:
        """Find all businesses in a "search results" page, call `parse_business_page` on each."""
        for url in response.xpath(GoudenGidsXPaths.LISTING).getall():
            # TODO(Ivan Yordanov): Using `SplashRequest` to read elements such as parking infor properly,
            # but it is not working at the moment. I suspect that it has something to
            # do with the args, and perhaps some settings in `settings.py`, but I am
            # not sure.
            # The goal is to wait for a little, so that the page has time to
            # load fully and then pass the now final HtmlResponse to the functions
            # that scrape the data off of it.
            yield SplashRequest(
                BASE_URL + url, callback=self.parse_business_page, args={"wait": 3}
            )

    def parse_business_page(self, response: HtmlResponse) -> Iterator[BusinessItem]:
        """Yield item containing all scraped details bout a business."""
        # This is the object that contains all the scraped data for a business.
        # For each of its attributes I use one of the functions that I have defined
        # further down together with an XPath from that enum class at the top of the file.
        # The enum's strengths shine here -- notice how instead of long ugly strings
        # we have meaningful names such as name, location, etc.
        # We also hopefully wouldn't need to touch this function at all suppose the path
        # to a section changes and XPaths need to be modified. That can happen in
        # `GoudenGidsXPaths` where each string is assigned to a clear name, immediately
        # making it clear what its general meaning is.
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
            # Solvable using Splash or Selenium.
            # For now I have chosen Splash, because the library is slightly better maintained.
            # `scrapy-selenium` has been dead for ~3 years while `scrapy-splash`
            # was last updated in February 2023.
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
            logo=self.get_element_text(response, GoudenGidsXPaths.LOGO_SRC),
            pictures=self.get_element_texts(response, GoudenGidsXPaths.PHOTO_SRC),
        )
        # Since `business_item` is a scrapy.Item instance, scrapy knows to collect
        # it and write it to the `.csv` file that we have defined in the settings.
        yield business_item

    # Method is static, because it doesn't need to access anything from `self`
    # The code is gonna be a bit easier to read and no needless operations would
    # be performed. Same for the static methods below.
    @staticmethod
    def get_element_text(response: HtmlResponse, xpath: str) -> str:
        """Return the text contained in the element towards which a provided xpath points."""
        # use `or` to ensure that the return type is `str`
        return response.xpath(f"normalize-space({xpath})").get() or ""

    @staticmethod
    def get_element_texts(response: HtmlResponse, xpath: str) -> list[str]:
        """Return the texts contained in the element towards which a provided xpath points."""
        # In some places there are a couple elements that we can just retrieve in a list
        # For those, it is hard to use `normalize-space()` in the XPath, especially because
        # scrapy uses XPath 1.0. Hence, we use Python's string manipulation abilities
        # to remove all redundant whitespace from the texts
        return [el.strip() for el in response.xpath(xpath).getall()] or []

    # This method would have been static if it didn't have to call `get_element_text`.
    # Neatly, we can make it a class method. It doesn't need anything from
    # an instance, it only needs a static method, so instead of binding `get_working_times`
    # to each instance of its class, we bind it just once to the class itself.
    @classmethod
    def get_working_times(cls, response: HtmlResponse) -> WorkingTimeItem:
        """Return `WorkingTimeItem` containing the work time of a business."""

        # Here I have nested the function, because I see no place where
        # it could be used aside from here in `get_working_times`. This keeps the namespace
        # clean.
        def get_working_time_day(response: HtmlResponse, day: DutchWeekDay) -> str:
            """Return the working time for a single day."""
            return cls.get_element_text(
                response, GoudenGidsXPaths.WORKING_DAY.format(day=day)
            )
        # Note how this function returns a `scrapy.Item`, instead of
        # yielding it. This is important as the `WorkingTimeItem` is intended
        # to be just a part of the BusinessItem.
        #
        # The code repetition is rather annoying here. There is a way to
        # avoid it, but since I am not 100% sure how it would be best to do it,
        # I prefer to leave as is for the moment until I have a little time to tinker with it.
        return WorkingTimeItem(
            monday=get_working_time_day(response, DutchWeekDay.MONDAY),
            tuesday=get_working_time_day(response, DutchWeekDay.TUESDAY),
            wednesday=get_working_time_day(response, DutchWeekDay.WEDNESDAY),
            thursday=get_working_time_day(response, DutchWeekDay.THURSDAY),
            friday=get_working_time_day(response, DutchWeekDay.FRIDAY),
            saturday=get_working_time_day(response, DutchWeekDay.SATURDAY),
            sunday=get_working_time_day(response, DutchWeekDay.SUNDAY),
        )

    @staticmethod
    def get_other_information(
        response: HtmlResponse,
        sections_xpath: str,
        section_name_xpath: str,
        section_value_xpath: str,
    ) -> dict[str, Any]:
        """Return a mapping of section/ names and values.

        Useful for a number of similar elements which contain separately
        the name of a piece of information and the actual information, such as
        provided services by the business, working times, etc.

        :param response: Response object to select information from.
        :param sections_xpath: XPath that points towards an element containing
            a mapping-like structure
        :param section_name_xpath: XPath that points to the elements containing
            names/titles. Should start where `sections_xpath` ends.
        :param section_value_xpath: XPath that points to the elements containing
            the piece of information.
        :return: Dictionary containing the corresponding data.
        """
        # This is almost a combination of the 2 simpler static methods above
        # I would try to remove the repeated logic here.
        return {
            section.xpath(section_name_xpath).get() or "": [
                el.strip() for el in section.xpath(section_value_xpath).getall()
            ]
            for section in response.xpath(sections_xpath)
        }
