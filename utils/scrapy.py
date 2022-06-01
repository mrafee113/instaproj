import os
import json
import termcolor
import functools
import termcolor
import urllib.parse

from typing import Union
from functools import partial
from scrapy.crawler import CrawlerRunner
from scrapy.exceptions import UsageError
from selenium.webdriver.common.by import By
from scrapy.crawler import CrawlerProcess, Crawler
from django.conf import settings as django_settings
from scrapy.utils.project import get_project_settings
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def handler_decorator(func):
    """This only works for @classmethod"""

    @functools.wraps(func)
    def wrapper_handler(cls, el: Union[WebElement, WebDriver, None], repetitive: Union[bool, int] = 3,
                        raise_exception=False, **kwargs):
        if repetitive is False:
            repetitive = 1

        counter = 0
        response = None
        while counter < repetitive:
            response = func(cls, el, **kwargs)
            if response is not None:
                break

            counter += 1

        if raise_exception and (response is None or response is False):
            raise Exception("Operation Failed.")
        return response

    return wrapper_handler


class ScrapyHandler:
    """When a method is called, arguments from
    "handler_decorator.wrapper_handler" should be
    taken into account. Specially positional arguments.
    """

    @classmethod
    @handler_decorator
    def get_element(cls, el: Union[WebElement, WebDriver], xpath: str, many=False) \
            -> Union[WebElement, None, list[WebElement]]:
        try:
            if many:
                return el.find_elements(By.XPATH, xpath)
            return el.find_element(By.XPATH, xpath)
        except Exception:  # noqa
            pass

    @classmethod
    @handler_decorator
    def get_attr(cls, el: Union[WebElement, WebDriver, None], attr: str, prop=False) \
            -> Union[str, None]:
        try:
            if prop:
                return getattr(el, attr)
            else:
                return el.get_attribute(attr)
        except Exception:  # noqa
            pass

    @classmethod
    @handler_decorator
    def call_attr(cls, el: Union[WebElement, WebDriver, None], attr: str, **kwargs) -> bool:
        try:
            getattr(el, attr)(**kwargs)
            return True
        except Exception:  # noqa
            return False

    @classmethod
    def extract_from_list(cls, value: list, raise_exception=False):
        valid = True
        reason = str()
        if isinstance(value, list):
            if len(value) < 1:
                valid = False
                reason = 'iterable has length < 1'
            elif len(value) > 1:
                valid = False
                reason = 'iterable has length > 1'
                print(termcolor.colored(f'SelectorList had more than one element. invalidated. {value}'))
            else:
                value = value[0]
        else:
            valid = False
            reason = f'type of value was not of type list. type(value)={type(value)}'

        if not valid:
            if raise_exception:
                raise TypeError(f'invalidated. reason="{reason}" value={value}')
            else:
                return None
        return value

    @classmethod
    def validate(cls, value, none=True, tipe=None, value_exc=None, validation=None, post=None):
        from utils.selenium import DriverHandler
        valid = DriverHandler.validate(value, none=none, tipe=tipe, value_exc=value_exc, validation=validation)
        if valid:
            if post is not None:
                value = post(value)
            return value

        return None

    @classmethod
    def pvalidate(cls, none=True, tipe=None, value_exc=None, validation=None, post=None):
        kw = {"none": none, 'tipe': tipe, "value_exc": value_exc, "validation": validation, "post": post}
        kw = {k: v for k, v in kw.items() if v is not None}
        if kw:
            return partial(cls.validate, **kw)

    @classmethod
    def add_validated(cls, store: dict, key: str, value, post=None,
                      none=True, tipe=None, value_exc=None, validation=None) -> bool:
        from utils.selenium import DriverHandler
        return DriverHandler.add_validated(store, key, value, post=post, none=none, tipe=tipe, value_exc=value_exc,
                                           validation=validation)

    @classmethod
    def urlify(cls, scheme=str(), netloc=str(), path=str(), params=str(), query=str(), fragment=str()) -> str:
        return urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment))


# todo: create timer decorator
# todo: add logging
# todo: add testing... maybe? maybe not?
def scrapy_crawler(spider_name: str, **spider_kwargs):
    cur_dir = os.getcwd()
    os.chdir(os.path.join(django_settings.BASE_DIR, 'scrapy_scrapers'))
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_scrapers.settings'
    settings = get_project_settings()
    spider_loader = CrawlerRunner._get_spider_loader(settings)
    spider_klass = spider_loader.load(spider_name)

    process = CrawlerProcess(settings)
    crawler = Crawler(spider_klass, settings=settings)
    process.crawl(crawler, **spider_kwargs)
    process.start()
    os.chdir(cur_dir)
    return {'settings': settings, 'process': process, 'crawler': crawler, 'spider_class': spider_klass}


def parse_symbols_or_indexes_argument(symbols: Union[None, str, list[str]], raise_exception=True) -> Union[
    None, str, list[str]]:
    if isinstance(symbols, str) and symbols != 'all':
        try:
            symbols = json.loads(symbols)
        except json.JSONDecodeError:
            pass

    valid = ScrapyHandler.validate(symbols, tipe=list, value_exc=list()) and \
            all(map(lambda x: ScrapyHandler.validate(x, tipe=str, value_exc=str()), symbols))
    if not valid and symbols != 'all' and isinstance(symbols, str):
        if raise_exception:
            raise UsageError(f'symbols={symbols} is invalid. '
                             f'It has to be either "all" or a json-serializable list of strings.')
        return

    return symbols if valid or symbols == 'all' else 'all'


def debug_print(*s, c='cyan'):
    print(termcolor.colored(' '.join(list(map(str, s))), c))
