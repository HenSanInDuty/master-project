import scrapy

class CareerbuilderSpider(scrapy.Spider):
    name = 'DA_topdev'
    allowed_domains = ['topdev.vn']
    custom_settings = {
		'FEEDS': { 'ayda.csv': { 'format': 'csv', 'overwrite': True}}
		}
    rotate_user_agent = True
    
    def start_requests(self):
        yield scrapy.Request(url='https://topdev.vn/viec-lam-it?src=topdev_home&medium=search',
                             callback=self.parse)

    def parse(self, response):
        for job in response.css(".mt-4 .mb-4"):
            detail_url = "https://topdev.vn/" + job.css(".line-clamp-1 a.text-lg").xpath("@href").get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, cb_kwargs={'job':job})
            break
            
    
    def parse_detail(self, response, job):
        job_decription = ''
        # for job_description_detail in response.css(".job-description__item"):
        #     job_decription+=job_description_detail.css("h3::text").get()+"<br><br>"
        #     for detail_content in job_description_detail.css("div.job-description__item--content").getall():
        #       job_decription+=detail_content+"<br>"
              
        # job_tags = ''
        # for job_tag in job.css(".skills").getall():
        #     print("==========================JOB TAG")
        #     print(job_tag)
        print(job.get())
        yield {
            'job_title': job.css('h3.line-clamp-1 a::text').get(),
            'job_salary': job.css('div.title-block>label::text').get(),
            'job_decription': job_decription,
            'job_tags': "job.css('')",
            'company_address': "job.css('')",
            'company_name': job.css('div.body>a').xpath('@title').get(),
            'company_size': response.css('#job-detail > div.job-detail__wrapper > div > div.job-detail__body-right > div.job-detail__box--right.job-detail__company > div.job-detail__company--information > div.job-detail__company--information-item.company-scale > div.company-value::text').get()
        }
