import scrapy
import re
import logging
from scrapy.utils.log import configure_logging 

class VNExpressSpider(scrapy.Spider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    name = 'vnexpress'
    allowed_domains = ['vnexpress.net']
    custom_settings = {
		'FEEDS': { 'data_crawl.json': { 'format': 'json', 'overwrite': True}}
		}
    rotate_user_agent = True
    
    # Lấy 20 trang của web
    max_page = 20
    
    urls = {
        "ThoiSu":"https://vnexpress.net/thoi-su",
        "TheGioi":"https://vnexpress.net/the-gioi",
        "KinhDoanh":"https://vnexpress.net/kinh-doanh",
        "BatDongSan":"https://vnexpress.net/bat-dong-san",
        "KhoaHoc":"https://vnexpress.net/khoa-hoc",
        "GiaiTri":"https://vnexpress.net/giai-tri",
        "TheThao":"https://vnexpress.net/the-thao",
        "PhapLuat":"https://vnexpress.net/phap-luat",
        "GiaoDuc":"https://vnexpress.net/giao-duc",
        "SucKhoe":"https://vnexpress.net/suc-khoe",
        "DoiSong":"https://vnexpress.net/doi-song",
        "DuLich":"https://vnexpress.net/du-lich",
        "SoHoa":"https://vnexpress.net/so-hoa",
        "Xe":"https://vnexpress.net/oto-xe-may",
    }
    
    item = {
        'url',
        'title',
        'datetime',
        'content',
        'description'
    }
    
    data_crawl = []
    
    def start_requests(self):
        for topic in self.urls.keys():
            yield scrapy.Request(url=self.urls[f'{topic}'],
                             callback=self.parse, cb_kwargs={'topic':topic, 'page':1})

    def parse(self, response, topic, page):
        articles_css_selector = f'article.item-news.item-news-common.thumb-left:not([class*="close_not_qc"])'
        for news_card in response.css(articles_css_selector):
            try:    
                element_contain_href = ".title-news > a"
                # Lấy trang chi tiết 
                detail_url = news_card.css(element_contain_href).xpath("@href").get()
                yield scrapy.Request(url=detail_url, callback=self.parse_detail, cb_kwargs={'detail_url':detail_url, 'topic': topic})
            except:
                logging.error("Logging Error at detail news: " + topic + " , page " + page)
        
        if page < self.max_page:
            next_page = self.urls[f'{topic}'] + f'-p{page+1}'
            try:
                yield scrapy.Request(url=next_page, callback=self.parse, cb_kwargs={'topic':topic, 'page':page+1})
            except:
                logging.error("Logging Error at next page: "+next_page)
                
    
    def parse_detail(self, response, detail_url, topic):
        news_content_section_css = 'section.page-detail.top-detail'
        news_content = response.css(news_content_section_css)
        sub_topic = news_content.css('ul.breadcrumb > li:nth-of-type(2) > a::text').get()
        title = news_content.css('h1.title-detail::text').get()
        datetime = news_content.css('span.date::text').get()
        description = news_content.css('p.description::text').get()
        content = ''
        author = ''
        
        # Vì trang web có nhiều element để chứa content nên phải chạy hết (bỏ đi hình ảnh)
        main_article = news_content.css('article.fck_detail')
        all_text = list(main_article.css('p'))
        for i in range(len(all_text)):
            if i < len(all_text) - 1:
                content += all_text[i].css('::text').get()
            else:
                # Xóa html tag
                p = re.compile(r'<.*?>')
                author = p.sub('', str(all_text[i]))
                author = author.replace("\n","").strip()

        data = {
            'topic': topic,
            'sub-topic': sub_topic,
            'url': detail_url,
            'title': title,
            'datetime': datetime,
            'content': content,
            'description': description,
            'author': author
        }
        
        yield data
