

# LRCforumIndex spider
import scrapy
import re
from LRC.items import LRCforumItem


class TopicSpider(scrapy.Spider):
    name = "Topics"
    allowed_domains = ["letsrun.com"]
    start_urls = ["http://www.letsrun.com/forum/forum.php?board=1"]

    # Example of one index entry
    """
    <li class="row">
    <div class="post_count">3</div>
    <div class="timestamp"><em>2/11/2016 6:45pm</em></div>
    <div class="title ">
    <span class="post_title"><a href="http://www.letsrun.com/forum/flat_read.php?thread=7028666">RAK Half Marathon 10 PM Eastern </a></span><span class="post_dash"> - </span><span class="post_author">Matta99</span></div>
    <div class="post_meta_mobile">Matta99 (2/11/2016 6:45pm, 3 posts)</div></li>
    """

    def parse(self, response):

        for sel in response.xpath("//li[@class='row']"):
            item = LRCforumItem()
            item['post_count'] = (sel.xpath("div[@class='post_count']/text()")
                                  .extract())
            item['timestamp'] = (sel.xpath("div[@class='timestamp']/em/text()")
                                 .extract())

            tit = sel.xpath("div/span[@class='post_title']")

            item['title'] = tit.xpath("a/text()").extract()

            url_sel = tit.xpath("a/@href")
            item['url'] = url_sel.extract()
            item['post_id'] = url_sel.re("thread=(\d+)")
            # print("{}\n{}\n{}\n{}\n".format(timestamp, title, url, post_count))
            yield item
