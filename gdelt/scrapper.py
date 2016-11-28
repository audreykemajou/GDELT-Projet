from abc import ABC,abstractmethod
import aiohttp
import asyncio
import re
import json
import AdvancedHTMLParser
from .items import Article
from operator import itemgetter
import logging
from concurrent import futures
from time import perf_counter

logger = logging.getLogger(__name__)


class GDELT_Scrapper():
    def __init__(self, **kwargs):
        self.query = kwargs.get('query',None)
        self.last_results = set()


    def run(self,query=None, **kwargs:dict):
        """ The run method will be launched and shall return a list of items (e.g. Articles)
        """
        self.query = self.query if not query else query
        results = set()
        logger.info('querying {}'.format(self.query))
        results = self.run_single(self.query,**kwargs)
        self.last_results = results.copy()
        return results


    def run_single(self,query=None,**kwargs):
        articles = self.fetch_articles_all(query)

        worker_results = set()

        for article in articles:
            worker_results.add(Article(article.get('url'),query=query))

        return worker_results

    def fetch_articles_all(self, query=None):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        to_do = [self.async_fetch_articles(query)]
        wait_coroutines = asyncio.wait(to_do)
        res, _ = loop.run_until_complete(wait_coroutines)
        loop.close()

        results = [result.result() for result in res]

        article_list = self.parse_html(results)

        return article_list

    async def async_fetch_articles(self,query):
        query = query.replace(' ', '+')
        search_url = "http://api.gdeltproject.org/api/v1/search_ftxtsearch/search_ftxtsearch?query="+query+"&output=artimglist&dropdup=true"

        resp = await aiohttp.request('GET',search_url)
        content = await resp.text()
        return content

    def parse_html(self,results):
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        article_list = []
        for result in results:
            parser.parseStr(result)

            article_tags = parser.getElementsByTagName('a')

            articles = [{'url' : article_tag.getAttribute('href')} for article_tag in article_tags if article_tag.getAttribute('href').startswith('http')]
            logger.info("parse_html.images : {}".format([i.get('url') for i in articles]))
            article_list += articles
            #parser la page pour récupérer les liens des articles


        return article_list
