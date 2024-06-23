from scrapy import Field, Item


class WorkingTimeItem(Item):
    """Item that contains the days of the week."""

    monday = Field()
    tuesday = Field()
    wednesday = Field()
    thursday = Field()
    friday = Field()
    saturday = Field()
    sunday = Field()


class BusinessItem(Item):
    """Item that holds all information about a business."""

    name = Field()
    location = Field()
    description = Field()
    phone = Field()
    website = Field()
    email = Field()
    social_media = Field()
    payment_options = Field()
    certificates = Field()
    other_information = Field()
    working_time = Field()
    parking_info = Field()
    economic_data = Field()
    logo = Field()
    pictures = Field()
