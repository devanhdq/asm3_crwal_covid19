import scrapy
from scrapy_splash import SplashRequest


class CovidSpider(scrapy.Spider):
    name = "covid"

    # Đầu tiên, ta cần đưa URL đến trang web đầu tiên vào đối tượng SplashRequest
    def start_requests(self):
        url = 'https://web.archive.org/web/20210907023426/https://ncov.moh.gov.vn/vi/web/guest/dong-thoi-gian'
        yield SplashRequest(
            url,
            callback=self.parse
        )

    # Xử lý dữ liệu ở trang hiện tại
    # Lấy ra 3 thông tin gồm: date(ngày), case(số ca bệnh trong ngày), detail(danh sách ca bệnh theo từng tỉnh)
    def parse(self, response):

        for item in response.xpath("//div[@class ='timeline-sec']//ul"):
            time = item.xpath(".//li//div[@class='timeline-head']//h3//text()").get()
            case = item.xpath(".//li//div[@class='timeline-content']//p[position()=2]//text()").get()
            detail = item.xpath(".//li//div[@class='timeline-content']//p[position()=3]//text()").get()

            yield {
                "time": time,
                "case": case,
                "detail": detail
            }

        # lấy ra button "Tiếp theo"
        next = response.xpath(
            "//ul[@class='lfr-pagination-buttons pager']//li[position()=2][not(@class='disabled')]//a")

        # kiểm tra xem nút "Tiếp theo" có khả dụng không, nếu có thì nhấn vào nút đó và cập nhật lại URL mới
        if next:
            yield SplashRequest(
                url=response.url,
                callback=self.parse,
                args={
                    'lua_source': f"""
                        function main(splash, args)
                              assert(splash:go(args.url))
                              local element = splash:select('.lfr-pagination-buttons > li:nth-of-type(2) > a')
                              element:mouse_click()
                              splash:wait(10)
                            return {{ url = splash:url() }}
                        end
                    """
                }
            )
