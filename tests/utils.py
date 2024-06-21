from pathlib import Path

from scrapy.http import HtmlResponse, Request


def read_response_from_file(file_path: Path, url: str):
    """Create a Scrapy fake HTTP response from a HTML file.

    :param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    :param url: The URL of the response.
    :return: A scrapy HTTP response which can be used for unittesting.
    """
    if not file_path.is_absolute():
        file_path = Path(__file__).parent.resolve() / file_path
    return HtmlResponse(
        url=url,
        request=Request(url=url),
        body=file_path.read_text(),
        encoding="utf-8",
    )
