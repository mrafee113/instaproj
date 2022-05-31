import json

from lxml import html
from pathlib import Path
from django.conf import settings
from scrapy.spiders import Spider
from scrapy.http.request import Request
from scrapy.http.response import Response
from playwright.async_api._generated import Page
from itemadapter import ItemAdapter

from .items import ProfileLoader


class ProfileSpider(Spider):
    """
    Uses one url, which needs list[username: str] as argument.
    - Uses one request per username.
    - Uses 10 simultaneous concurrent requests.
    Output: list[dict] :: dumped in /tmp/ig_username_info
        :after scraping -> use scrapy_scrapers.spiders.post_scripts.add_ig_user_info_to_db
    Dictionary Keys: username, media_count, follower_count, following_count,
        full_name, category_name, biography, external_url
    """

    name = 'profile_spider'
    allowed_domains = ['instagram.com']
    custom_settings = {
        'CONCURRENT_REQUESTS': 10,
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_scrapers.middlewares.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_scrapers.middlewares.ScrapyPlaywrightDownloadHandler'
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def __init__(self, *a, usernames: str, **kw):
        super().__init__(*a, **kw)
        if usernames.startswith("'") or usernames.endswith("'"):
            usernames = usernames.strip("'")
        self.usernames: list[str] = json.loads(usernames)

    USERAGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
    URL = 'https://www.instagram.com/{username}/'

    def start_requests(self):
        for username in self.usernames:
            url = self.URL.format(username=username)
            meta = {
                'playwright': True,
                'playwright_include_page': True,
                'playwright_context_kwargs': {
                    'user_data_dir': settings.CHROME_USER_DATA_DIR
                }
            }
            yield Request(url=url, callback=self.parse, cb_kwargs={'username': username},
                          errback=self.errback_close_page, meta=meta)

    @classmethod
    async def errback_close_page(cls, failure):
        await failure.requst.meta('playwright_page')

    async def parse(self, response: Response, **kwargs):
        page: Page = response.meta['playwright_page']

        # parse
        inner_html = await page.inner_html('//body')
        inner_html = f'<html><body>{inner_html}</body></html>'
        doc: html.HtmlElement = html.document_fromstring(inner_html)

        loader = ProfileLoader()
        main_xpath = '//body//main[@role="main"]/div/header/section'

        media_count = doc.xpath(f'{main_xpath}/ul/li[1]/div/span')[0].text_content()
        loader.add_value('media_count', media_count)

        follower_count = doc.xpath(f'{main_xpath}/ul/li[2]/a/div/span')[0].text_content()
        loader.add_value('follower_count', follower_count)

        following_count = doc.xpath(f'{main_xpath}/ul/li[3]/a/div/span')[0].text_content()
        loader.add_value('following_count', following_count)

        full_name = doc.xpath(f'{main_xpath}/div[3]/span')[0].text_content()
        loader.add_value('full_name', full_name)

        category_name = doc.xpath(f'{main_xpath}/div[3]/div[@class="_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p _abcm"]/div')
        category_name = category_name[0].text_content() if category_name else None
        loader.add_value('category_name', category_name)

        biography = doc.xpath(f'{main_xpath}/div[3]/div[@class="_aacl _aacp _aacu _aacx _aad6 _aade"]')
        biography = biography[0].text_content() if biography else None
        loader.add_value('biography', biography)

        external_url = doc.xpath(f'{main_xpath}/div[3]/a/div')
        external_url = 'https://' + external_url[0].text_content() if external_url else None
        loader.add_value('external_url', external_url)

        username = response.cb_kwargs['username']
        loader.add_value('username', username)

        item = loader.load_item()
        folder = settings.DATA_PATH / 'ig_user_info'
        folder.mkdir(exist_ok=True)
        with open(folder / f'{username}.json', 'w') as file:
            adapter = ItemAdapter(item)
            json.dump(dict(adapter), file)

        await page.close()
