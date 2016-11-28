from abc import ABC,abstractmethod
from time import perf_counter,time

import aiohttp
import asyncio
import json
import re
import logging
import os
import requests

logger = logging.getLogger(__name__)

class Article():
    """ Represent the data model that'll be used by all the scrappers"""
    def __init__(self,url:str,**kwargs):

        self.url = url

        self.query = kwargs.get('query',"")
        self.auto_storing = kwargs.get('store',True) #Set to false to cancel autostoring
        self.content = None
        self.path = None

        #logger.info('Init Image{}'.format(self.__dict__))

    def download(self):
        logger.info('Downloading: {}'.format(self.url))
        counter = perf_counter()
        if not self.content:
            resp = requests.get(self.url)
            self.content = resp.content
        logger.info('Done: {}  | Elapsed T.: {}'.format(self.url, perf_counter() - counter))
        if self.auto_storing:
            return self.store()
        return self.content

    async def async_download(self):
        """ Asynchronously download the associated self.url and returns the image content """

        logger.info('Downloading: {}'.format(self.url))
        counter = perf_counter()
        if not self.content:
            resp = await aiohttp.request('GET',self.url)
            self.content = await resp.read()
        logger.info('Done: {}  | Elapsed T.: {}'.format(self.url, perf_counter()-counter))

        if self.auto_storing:
            return self.store()
        return self.content

    def download_all(articleList):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        to_do = [article.async_download() for article in articleList]
        wait_coroutines = asyncio.wait(to_do)
        res, _ = loop.run_until_complete(wait_coroutines)
        loop.close()

    def to_json(self):
        output = self.__dict__.copy()
        output.pop('content')
        output.pop('auto_storing')
        return json.dumps(output)

    def store(self,path="tmp/"):
        if self.content is None:
            logging.error("Must proceed to download before storing the image.")
            return False

        #yield from aiohttp.request('POST') ?
        base_path = os.path.join(path,self.query).replace(' ', '-')
        logger.info('Storing... PATH={}'.format(base_path))
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        dest_path = os.path.join(base_path,str(time())+"_"+"gdelt")

        with open(dest_path,'wb') as file:
            file.write(self.content)

        logger.info('Done... PATH={}'.format(dest_path))
        self.path = dest_path
        return dest_path
