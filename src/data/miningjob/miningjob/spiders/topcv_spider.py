import scrapy

class CareerbuilderSpider(scrapy.Spider):
    name = 'topcv'
    allowed_domains = ['topcv.vn']
    custom_settings = {
		'FEEDS': { 'Final_TopCV.csv': { 'format': 'csv', 'overwrite': True}}
		}
    rotate_user_agent = True
    
    def start_requests(self):
        yield scrapy.Request(url='https://www.topcv.vn/viec-lam-it',
                             callback=self.parse)

    def parse(self, response):
        next_page = response.css(".pagination > li:nth-child(15) > a:nth-child(1)").xpath("@href").get()
        for job in response.css("div.job-item-2"):
            detail_url = job.css("div.title-block>h3>a").xpath("@href").get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, cb_kwargs={'job':job})
            
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
    
    def parse_detail(self, response, job):
        job_decription = ''
        for job_description_detail in response.css(".job-description__item"):
            job_decription+=job_description_detail.css("h3::text").get()+"<br><br>"
            for detail_content in job_description_detail.css("div.job-description__item--content").getall():
              job_decription+=detail_content+"<br>"
              
        job_tags = ''
        for job_tag in job.css(".skills > .item"):
            if ("title" in job_tag.attrib.keys()):
                job_tags += f"{job_tag.xpath('@title').get()}"
            else:
                job_tags += f'{job_tag.xpath("text()")[0].get()}, '
            
        yield {
            'job_id': job.xpath('@data-job-id').get(),
            'job_title': job.css('div.title-block>h3>a>span::text').get(),
            'job_salary': job.css('div.title-block>label::text').get(),
            'job_decription': job_decription,
            'job_tags': job_tags,
            'company_address': job.css('label.address').xpath('string(.)').get().replace(f'\n', '').strip(),
            'company_name': job.css('div.body>a').xpath('@title').get(),
            'company_size': response.css('#job-detail > div.job-detail__wrapper > div > div.job-detail__body-right > div.job-detail__box--right.job-detail__company > div.job-detail__company--information > div.job-detail__company--information-item.company-scale > div.company-value::text').get()
        }
