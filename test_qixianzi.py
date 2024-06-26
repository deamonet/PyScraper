"""
用来爬取 https://www.qixianzi.com/Korea/56954.html 的图片
采用微软的playwright WEB 自动化测试框架
"""
import os.path
import yaml
import zipfile
from typing import Callable

from playwright.sync_api import Page
import logging

LOGGER = logging.getLogger(__name__)
DELIMITER = "-+="
NEW_LINE = "\n"


def produce_job_urls(url_prefix: str, start: int, end: int):
    html_extension = ".html"
    ls = set()
    for i in range(start, end + 1):
        ls.add(url_prefix + "_" + str(i) + html_extension)
    return ls


def scrape_qixianzi_image(url: str, page: Page):
    page.goto(url)
    element = page.locator("xpath=//html/body/div/div/div/div[1]/div/div[2]/a/img")
    return element.get_attribute("src")


def scrape_images(job_urls: list[str], page: Page, save_file: str, func: Callable):
    for job_url in job_urls:
        with open(save_file, "a") as fi:
            url = job_url + DELIMITER + func(job_url, page) + NEW_LINE
            LOGGER.info(url)
            fi.write(url)


def main_flow(base_url, save_file, start, end, page: Page):
    done_url = set()
    if os.path.exists(save_file):
        fi = open(save_file, "r")
        for line in fi.readlines():
            done_url.add(line.split(DELIMITER)[0])
    else:
        fi = open(save_file, "w")
        fi.close()

    job_urls = [url for url in produce_job_urls(base_url, start, end) if url not in done_url]
    LOGGER.info("REMAINING JOBS:")
    for job in job_urls:
        LOGGER.info(job)
    scrape_images(job_urls, page, save_file, scrape_qixianzi_image)


def recalculate_scraped_image_total(save_file):
    with open(save_file, "r") as fi:
        return len(set(fi.readlines()))


def test_qixianzi(page: Page):
    with open("application.yml", "r", encoding="utf-8") as fi:
        application_config = yaml.safe_load(fi)

    base_url = application_config['application']['base_url']
    save_file = application_config['application']['save_file']
    start = application_config['application']['iteration']['from']
    end = application_config['application']['iteration']['to']
    image_total = end + 1
    while recalculate_scraped_image_total(save_file) < image_total:
        try:
            main_flow(base_url, save_file, start, end, page)
        except Exception as e:
            LOGGER.error("FAILURE", e)


def image_download(url: str, path: str, page: Page):
    image_file_name = url.split("/")[-1]
    with open(f"{path}/{image_file_name}", "wb") as fi:
        fi.write(page.goto(url).body())


def images_download(urls: set[str], path: str, page: Page):
    for url in urls:
        image_download(url, path, page)


def download_main_flow(path: str, page: Page):
    done_images = {}
    for root, dirs, files in os.walk("./images"):
        done_images = set(files)

    with open("save_file_copy.txt", "r") as fi:
        work_images = {line.strip() for line in fi.readlines() if line.split("/")[-1].strip() not in done_images}

    images_download(work_images, path, page)


def calculate_images(path: str):
    done_images = {}
    for root, dirs, files in os.walk("./images"):
        done_images = set(files)
    return len(done_images)


def test_qixianzi_image_download(page: Page):
    path = "./images"
    while calculate_images(path) < 100:
        try:
            download_main_flow(path, page)
        except Exception as e:
            LOGGER.info("FAILURE, RESTART...", e)


if __name__ == "__main__":
    download_main_flow("./imagesd", None)
