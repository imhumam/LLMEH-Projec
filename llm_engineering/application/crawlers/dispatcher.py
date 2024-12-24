import re
from urllib.parse import urlparse
from loguru import logger

from .base import BaseCrawler
from .custom_article import CustomArticleCrawler
from .github import GithubCrawler
from .linkedin import LinkedInCrawler
from .medium import MediumCrawler




"""
The entry point to our crawling logic is the CrawlerDispatcher class.
The dispatcher acts as the intermediate layer between the provided links and the crawlers.

The CrawlerDispatcher class knows how to extract the domain of each link 
and initialize the proper crawler that collects the data from that site.

"""
class CrawlerDispatcher:
    def __init__(self) -> None:
        self._crawlers = {}

    @classmethod
    def build(cls) -> "CrawlerDispatcher":
        dispatcher = cls()
        return dispatcher

    def register_medium(self) -> "CrawlerDispatcher":
        self.register("https://medium.com", MediumCrawler)

        return self

    def register_linkedin(self) -> "CrawlerDispatcher":
        self.register("https://linkedin.com", LinkedInCrawler)

        return self

    def register_github(self) -> "CrawlerDispatcher":
        self.register("https://github.com", GithubCrawler)

        return self
    

    # Normalizes each domain to ensure its format is consistent before it’s 
    # added as a key to the self._crawlers registry  of the dispatcher.
    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        parsed_domain = urlparse(domain)
        domain = parsed_domain.netloc
        self._crawlers[r"https://(www\.)?{}/*".format(re.escape(domain))] = crawler


    # Determines the appropriate crawler for a given URL by matching
    # it against the registered domains. If no match is found, 
    # it logs a warning and defaults to using the CustomArticleCrawler
    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
            else:
                logger.warning(f"No crawler found for {url}. Defaulting to
            CustomArticleCrawler.")
            return CustomArticleCrawler()