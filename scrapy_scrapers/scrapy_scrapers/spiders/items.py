from scrapy.item import Item, Field
from utils.scrapy import ScrapyHandler as H
from utils.itemloader import TFCompose, ItemLoader


class ProfileItem(Item):
    username: str = Field()
    media_count: int = Field()
    follower_count: int = Field()
    following_count: int = Field()
    full_name: str = Field()
    category_name: str = Field()
    biography: str = Field()
    external_url: str = Field()


class ProfileLoader(ItemLoader):
    default_item_class = ProfileItem

    @staticmethod
    def process_number_string(number: str) -> int:
        if 'K' in number.upper():
            multiplier = 10 ** 3
        elif 'M' in number.upper():
            multiplier = 10 ** 6
        else:
            multiplier = 1

        number = number.upper().replace('M', '').replace('K', '').replace(',', '').strip()
        return int(float(number) * multiplier)

    text_processor = TFCompose(H.pvalidate(tipe=str, value_exc=str()))
    int_processor = TFCompose(H.pvalidate(tipe=str), str.strip, process_number_string)

    media_count_in = int_processor
    follower_count_in = int_processor
    following_count_in = int_processor
    full_name_in = text_processor
    category_name_in = text_processor
    biography_in = text_processor
    external_url_in = text_processor
