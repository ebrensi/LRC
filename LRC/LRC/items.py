# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LRCforumIndex(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    post_id = scrapy.Field()
    url = scrapy.Field()
    num_posts = scrapy.Field()
    last_post = scrapy.Field()
