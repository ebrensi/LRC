

# LRCforumIndex spider
import scrapy
import re
from LRC.items import LRCforumItem


class TopicSpider(scrapy.Spider):
    MAX_PAGES = 10
    count = 0

    name = "Topics"
    allowed_domains = ["letsrun.com"]
    start_urls = ["http://www.letsrun.com/forum/forum.php?board=1"]

    def parse(self, response):
        for sel in response.xpath("//li[@class='row']"):
            item = LRCforumItem()
            item['count'] = (sel.xpath("div[@class='post_count']/text()")
                             .extract())
            item['timestamp'] = (sel.xpath("div[@class='timestamp']/em/text()")
                                 .extract())

            item['author'] = (sel.xpath("div/span[@class='post_author']/text()")
                              .extract())

            tit = sel.xpath("div/span[@class='post_title']")

            item['title'] = tit.xpath("a/text()").extract()

            url_sel = tit.xpath("a/@href")
            # item['url'] = url_sel.extract()
            item['post_id'] = url_sel.re("thread=(\d+)")

            yield item

        next_page = response.xpath(
            "//nav/ul[@class='pagination']/li/a[text()='\xbb']/@href")

        if next_page and (self.count < self.MAX_PAGES):
            url = response.urljoin(next_page[0].extract())
            # url = next_page[0].extract()
            self.count += 1
            yield scrapy.Request(url, self.parse)
