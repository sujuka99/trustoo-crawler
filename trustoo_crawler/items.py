from scrapy import Field, Item


class BusinessItem(Item):
    name = Field()
    location = Field()
    description = Field()
    phone = Field()
    website = Field()
    email = Field()
    social_media = Field()
    hourly_rate = Field()
    payment_options = Field()
    certificates = Field()
    other_information = Field()
    working_time = Field()
