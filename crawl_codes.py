import scrapy
import os
from scrapy.crawler import CrawlerProcess

class GetBotSpider(scrapy.Spider):
    name = "GetBotSpider"
    baseUrl = "http://www.rpscontest.com"
    baseLeaderboard = "http://www.rpscontest.com/leaderboard/"
    start_urls = [ baseLeaderboard+str(i) for i in xrange(1,5) ] # 4 pages

    def save(self, name, rating, code):
        folder = "bots_crawl"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = folder+"/bot_"+str(rating)+"_"+name+".py"
        print( filename )
        with open(filename, "w+") as out:
            out.write(code)
            out.close()

    def parse_code(self, response):
        code = response.xpath("//code[@class='lang-py']/text()").extract_first()
        bot_name = response.xpath("//div/h1/text()").extract_first().replace(' ','_')
        bot_rating = response.xpath("//tr[3]/td[2]/text()").extract_first().strip()
        self.save(bot_name, bot_rating, code)

    def parse(self, response):
        table = response.xpath("//tr")[1:]
        for bot in table:
            url = self.baseUrl + bot.xpath("td/a/@href").extract_first()
            yield scrapy.Request(url=url, callback=self.parse_code)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(GetBotSpider)
process.start() # the script will block here until the crawling is finished
