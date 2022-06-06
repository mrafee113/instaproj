import asyncio
from typing import Optional
from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler as H, \
    BrowserContextWrapper, PERSISTENT_CONTEXT_PATH_KEY, logger, Crawler  # noqa
from pathlib import Path


class ScrapyPlaywrightDownloadHandler(H):
    async def _create_browser_context(
            self, name: str, context_kwargs: Optional[dict]
    ) -> BrowserContextWrapper:
        """Create a new context, also launching a browser if necessary."""
        if hasattr(self, "context_semaphore"):
            await self.context_semaphore.acquire()
        context_kwargs = context_kwargs or {}
        if context_kwargs.get(PERSISTENT_CONTEXT_PATH_KEY):
            context = await self.browser_type.launch_persistent_context(**context_kwargs)
            persistent = True
            self.stats.inc_value("playwright/context_count/persistent")
        else:
            await self._maybe_launch_browser()
            context = await self.browser.new_context(**context_kwargs)
            persistent = False
            self.stats.inc_value("playwright/context_count/non-persistent")
        context.on("close", self._make_close_browser_context_callback(name, persistent))
        logger.debug(f"Browser context started: '{name}' (persistent={persistent})")
        self.stats.inc_value("playwright/context_count")
        if self.default_navigation_timeout is not None:
            context.set_default_navigation_timeout(self.default_navigation_timeout)

        await context.add_cookies(self.COOKIES)
        self.contexts[name] = BrowserContextWrapper(
            context=context,
            semaphore=asyncio.Semaphore(value=self.max_pages_per_context),
            persistent=persistent,
        )

        self._set_max_concurrent_context_count()
        return self.contexts[name]

    def __init__(self, crawler: Crawler) -> None:
        super().__init__(crawler)
        settings = crawler.settings
        self.COOKIES = settings.get('INSTAGRAM_COOKIES')
