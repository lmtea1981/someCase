import requests
from bs4 import BeautifulSoup
import json

# 测试网页爬取
url = "https://thehackernews.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print("\n=== Page Content Preview ===")
    print(response.text[:1000])  # 打印前1000个字符
    
    # 解析网页
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 检查当前使用的选择器
    print("\n=== Testing Current Selectors ===")
    news_items = soup.find_all('div', class_='body-post clear')
    print(f"Found {len(news_items)} items with 'body-post clear' class")
    
    # 打印第一个匹配项的完整HTML
    if news_items:
        print("\n=== First Match HTML ===")
        print(news_items[0].prettify())
    
    # 尝试查找所有div元素，看看实际的页面结构
    print("\n=== Page Structure Overview ===")
    all_divs = soup.find_all('div', limit=20)
    for i, div in enumerate(all_divs):
        if 'class' in div.attrs:
            print(f"Div {i}: classes={div['class']}")
            if any('news' in cls.lower() or 'post' in cls.lower() for cls in div['class']):
                print(f"  Content preview: {div.text[:100]}...")
                print()
    
    # 检查是否有重定向
    if response.history:
        print("\n=== Redirect History ===")
        for resp in response.history:
            print(f"  {resp.status_code}: {resp.url}")
    
    # 尝试查找最新的新闻项目，使用不同的选择器
    print("\n=== Trying Alternative Selectors ===")
    # 查找包含新闻的主要容器
    main_content = soup.find('main') or soup.find('div', id='content')
    if main_content:
        print(f"Found main content: {main_content.name}{'#' + main_content['id'] if 'id' in main_content.attrs else ''}")
        # 在main内容中查找新闻项
        potential_news = main_content.find_all(['article', 'div'], limit=10)
        for i, item in enumerate(potential_news):
            if 'class' in item.attrs:
                classes = ' '.join(item['class'])
                if any(keyword in classes.lower() for keyword in ['story', 'news', 'post', 'item']):
                    print(f"  News candidate {i}: classes='{classes}'")
                    print(f"    Content: {item.text[:150]}...")
                    print()
                    
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except Exception as e:
    print(f"Error: {e}")
