import aiohttp
import asyncio
import faker
import requests


def construct_headers(**kwargs):
    fake = faker.Faker()
    kwargs['user-agent'] = fake.user_agent()
    return kwargs


async def scrape_old(url: str, host: str) -> str | None:
    headers = construct_headers(host=host)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if not response.ok:
                return

            return await response.text()


async def scrape(url: str, host: str, proxy: str):
    headers = construct_headers(host=host)
    proxies = {
        "http": proxy,
        "https": proxy
    }
    response = requests.get(url, headers=headers, proxies=proxies)
    if not response.ok:
        return
    return response.text


if __name__ == "__main__":
    url = "https://www.qixianzi.com/Korea/56954.html"
    host = "www.qixianzi.com"
    proxy = "http://omv.local:7890"
    html = asyncio.run(scrape_old(url, host))
    print(html)
