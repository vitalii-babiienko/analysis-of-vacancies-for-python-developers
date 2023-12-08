from datetime import date
from re import findall
from typing import Generator, Optional

import scrapy
from scrapy.http import Response

from config import months, technologies


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def parse(
        self,
        response: Response,
        **kwargs: Optional[dict]
    ) -> Generator:
        vacancy_links = response.css(
            ".job-list-item__link::attr(href)"
        ).getall()

        for vacancy_link in vacancy_links:
            yield scrapy.Request(
                url=response.urljoin(vacancy_link),
                callback=self.get_single_vacancy,
            )

        next_page = response.css(
            ".pagination > li:last-child > a::attr(href)"
        ).get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_single_vacancy(
        self,
        response: Response
    ) -> Generator:
        relocation_compensation_exists = bool(
            response.css(".bi-airplane + div::text").get()
        )
        test_task_exists = bool(
            response.css(".bi-pencil-square + div::text").get()
        )
        views_count = int(
            response.css(".text-muted").re_first(r"(\d+) перегляд")
        )
        applicant_count = int(
            response.css(".text-muted").re_first(r"(\d+) відгук")
        )

        yield {
            "title": response.css("h1::text").get().strip(),
            "salary": self.get_salary(response),
            "company": response.css(".job-details--title::text").get().strip(),
            "english_level": self.get_english_level(response),
            "experience_years": self.get_experience_years(response),
            "domain": self.get_domain(response),
            "job_type": response.css(".bi-building + div::text").get(),
            "company_type": response.css(".bi-exclude + div::text").get(),
            "country": self.get_country(response),
            "relocation_compensation_exists": relocation_compensation_exists,
            "test_task_exists": test_task_exists,
            "publication_date": self.get_publication_date(response),
            "views_count": views_count,
            "applicant_count": applicant_count,
            "technologies": self.get_technologies(response),
        }

    @staticmethod
    def get_salary(response: Response) -> list[int] | None:
        salary = response.css(".public-salary-item::text").get()

        if salary is not None:
            return [int(s) for s in findall(r"\d+", salary)]

    @staticmethod
    def get_english_level(response: Response) -> str | None:
        english_level = response.xpath(
            "//div[contains(text(), 'Англійська:')]/text()"
        ).get()

        if english_level is not None:
            return english_level.split(":")[1].strip()

    @staticmethod
    def get_experience_years(response: Response) -> int:
        experience_years = response.xpath(
            "//div[contains(text(), 'досвіду')]/text()"
        ).get()

        return int(experience_years.split()[0].replace("Без", "0"))

    @staticmethod
    def get_domain(response: Response) -> str | None:
        domain = response.xpath(
            "//div[contains(text(), 'Домен:')]/text()"
        ).get()

        if domain is not None:
            return domain.split(":")[1].strip()

    @staticmethod
    def get_country(response: Response) -> list[str] | None:
        country = response.css(".bi-geo-alt-fill + div > span::text").get()

        if country is not None:
            return sorted(c.strip() for c in country.strip().split(","))

    @staticmethod
    def get_publication_date(response: Response) -> date:
        date_text = response.css(
            ".text-muted"
        ).re_first(r"\d{1,2} [а-я]+ \d{4}")

        day, month, year = date_text.split()

        return date(
            year=int(year),
            month=months.index(month) + 1,
            day=int(day),
        )

    @staticmethod
    def get_technologies(response: Response) -> list[str]:
        description = response.css(".mb-4").get().lower()

        return [
            technology for technology in technologies
            if technology.lower() in description
        ]
