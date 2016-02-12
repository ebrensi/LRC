

# LRCforumIndex spider
import scrapy
import re
from LRC.items import LRCforumItem
MAX_PAGES = 10


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
        count = 0

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

            yield item

        next_page = response.xpath(
            "//nav/ul[@class='pagination']/li/a[text()='\xbb']/@href")

        if next_page and (count < MAX_PAGES):
            url = response.urljoin(next_page[0].extract())
            count += 1
            yield scrapy.Request(url, self.parse)

"""
<nav>
  <ul class="pagination">

    <li class="disabled"><a href="#">&laquo;</a></li><li class="active"><a href='#'>1</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=1">2</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=2">3</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=3">4</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=4">5</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=5">6</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=6">7</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=7">8</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=8">9</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=9">10</a></li><li><a href="http://www.letsrun.com/forum/forum.php?board=1&page=1">&raquo;</a></li>  </ul>
</nav>
"""
