from typing import Optional
from urllib.parse import urlparse, urljoin, urlunparse

from selenium import webdriver 
from selenium.webdriver import Chrome 

from bs4 import BeautifulSoup, Tag
import re
import httpx

BASE64_REGEX = r'^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))$'

options = webdriver.ChromeOptions() 
options.add_argument("--disable-gpu")
options.add_argument('headless')
options.page_load_strategy = "normal"

domain_evaluations = {
    'link[rel=canonical]': 'href',
    'meta[property="og:url"]': 'content',
    'meta[itemprop="description"]': 'content',
}

image_evaluations = {
    'meta[property="og:image"]': 'content',
    'meta[name="twitter:image"]': 'content',
    'link[rel="image_src"]': 'href',
    'link[rel="apple-touch-icon"]': 'href',
    'img': 'src'
}

favicon_evaluations = {
    'link[rel=icon]': 'href',
    'link[rel="shortcut icon"]': 'href',
    'link[rel=icon]': 'href',
    'link[rel="apple-touch-icon"],link[rel="apple-touch-icon-precomposed"]': 'href',
}

description_evaluations = {
    'meta[name="description"]': 'content',
    'meta[name="twitter:description"]': 'content',
    'meta[property="og:description"]': 'content',
    'meta[itemprop="description"]': 'content',
}

title_evaluations = {
    'meta[name="title"]': 'content',
    'meta[name="twitter:title"]': 'content',
    'meta[property="og:title"]': 'content',
    'meta[itemprop="title"]': 'content',
}

def extract_urls(text: str):
    return re.findall(r'(https?://[^\s/$.?#].[^\s]*)', text)

async def url_image_is_accessible(url: str):
    urls = extract_urls(url)
    if any(re.match(BASE64_REGEX, u) for u in urls):
        return True
    for u in urls:
        async with httpx.AsyncClient() as client:
            response = await client.get(u)
        content_type = response.headers.get("content-type")
        if re.match(r'image/.*', content_type):
            return True
    return False

async def url_is_valid(url: str):
    urls = extract_urls(url)
    if any(re.match(BASE64_REGEX, u) for u in urls):
        return True
    for u in urls:
        async with httpx.AsyncClient() as client:
            response = await client.get(u)
        if response.status_code == 200:
            return True
    return False

def can_parse_url(url: str):
    try:
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
    except ValueError:
        return False

async def evaluate_sources(
    head: Tag, 
    sources: dict[str, str]
) -> Optional[str]:
    for source in sources.keys():
        try: 
            tag = head.select_one(source)
            if tag is None: continue
            data = tag.get(sources[source])
            if data: return data
            return None
        except Exception as error: 
            print(error)
            return None
        

async def get_domain(
    head: Tag, 
    url: str
) -> Optional[str]:
    try: 
        domain_mames = await evaluate_sources(head, domain_evaluations)
        if domain_mames:
            return urlparse(
                domain_mames
            ).hostname.replace("www.", "")
        else:
            return urlparse(
                url
            ).hostname.replace("www.", "")
            
    except: return None

async def get_preview_image(
    page: BeautifulSoup, 
    url: str
) -> Optional[str]:
    try: 
        head = page.head
        image_source = await evaluate_sources(head, image_evaluations)
        if image_source and len(image_source) > 0:
            if can_parse_url(image_source): 
                return image_source
            
            join_url = urljoin(url, image_source)
            if await url_image_is_accessible(join_url): 
                return join_url
            
        image_source = page.select_one('img')
        if image_source: 
            return image_source.get('src')
            
        image_source = await get_favicon(head, url)
        if image_source: 
            return image_source
        
        return None
    except: return None

async def get_favicon(
    head: Tag, 
    url: str
) -> Optional[str]:
    try: 
        parsed_url = urlparse(url)
        favicon_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "/favicon.ico", "", "", ""))
        if await url_image_is_accessible(favicon_url): 
            return favicon_url
        
        favicon_url = await evaluate_sources(head, favicon_evaluations)
        if favicon_url and len(favicon_url) > 0:
            if can_parse_url(favicon_url): 
                return favicon_url
            
            join_url = urljoin(url, favicon_url)
            if await url_image_is_accessible(join_url): 
                return join_url
        return None
    except: return None
    
async def get_description(
    page: BeautifulSoup, 
) -> Optional[str]:
    try: 
        description_source = await evaluate_sources(page.head, description_evaluations)
        if not description_source:
            p_tag = page.select_one('body p')
            if not p_tag: 
                return None
            description_source = p_tag.contents[0]
            
        if len(description_source) < 1: 
            return None
        
        return description_source
    except: 
        return None

async def get_title(head: Tag):
    if head.title: return head.title.text
    return await evaluate_sources(head, title_evaluations)
    
async def suop_html_parser(html: str, url: str):
    page = BeautifulSoup(html, 'html.parser')
    head = page.head
    current_url = url
    page_title = await get_title(head)
    domain = await get_domain(head, url)
    image = await get_preview_image(page, url)
    description = await get_description(page)
    
    return {
        "url": current_url, 
        "domain": domain,
        "title": page_title,
        "image": image,
        "description": description
    }

async def simple_requester(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    content = await suop_html_parser(response.content, url)
    return content

async def selenium_requester(url):
    driver = Chrome(options=options) 
    driver.get(url) 
    content = await suop_html_parser(driver.page_source, url)
    driver.quit()
    return content

async def get_url_preview(url):
    data = await simple_requester(url)
    
    if not data.get('image') or not data.get('title'):
        print("Requesting url through Selenium")
        data = await selenium_requester(url)

    return data