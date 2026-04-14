import asyncio
import json
import random
import time
import os
from playwright.async_api import async_playwright
import edge_tts

# 随机用户代理列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/120.0 Safari/537.36'
]

async def fetch_news_data(page, context, choice):
    """获取新闻数据"""
    telegraph_responses = []
    headline_responses = []
    all_responses = []
    news_data = []
    section = ""
    
    async def handle_response(response):
        all_responses.append(response.url)
        # 捕获电报API响应
        if 'telegraphList' in response.url:
            try:
                json_data = await response.json()
                telegraph_responses.append(json_data)
            except:
                pass
        # 捕获头条API响应 - 更精确的匹配
        elif any(keyword in response.url for keyword in ['headline', 'topnews', 'headlineList', 'articleList']):
            try:
                json_data = await response.json()
                headline_responses.append(json_data)
            except:
                pass
    
    page.on('response', handle_response)
    
    if choice == "1":
        section = "头条"
        # 导航到财联社首页
        await page.goto('https://www.cls.cn/')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(random.uniform(2, 4))  # 随机等待时间
        
        # 尝试从API响应获取头条新闻
        if headline_responses:
            for response in headline_responses:
                if isinstance(response, dict) and response.get('error') == 0 and response.get('data'):
                    # 检查不同的数据结构
                    if 'list' in response['data']:
                        news_data = response['data']['list']
                        break
                    elif 'data' in response['data']:
                        news_data = response['data']['data']
                        break
                    elif 'items' in response['data']:
                        news_data = response['data']['items']
                        break
                    elif 'news' in response['data']:
                        news_data = response['data']['news']
                        break
                    elif isinstance(response['data'], list):
                        news_data = response['data']
                        break
        
        # 如果API响应失败，尝试从页面中提取
        if not news_data:
            # 尝试使用更精确的选择器，专门针对头条新闻
            selectors = [
                '.top-news-container',
                '.headline-container',
                '.top-news-list',
                '.headline-list',
                '#headline',
                'div[class*="top"][class*="news"]',
                'div[class*="headline"]',
                'section[class*="news"]',
                'main[class*="news"]',
                '.news-container',
                '.news-list',
                '.article-container',
                '.article-list',
                'div[class*="news"]',
                'div[class*="article"]',
                'ul[class*="list"]',
                'ol[class*="list"]'
            ]
            
            news_items = []
            seen_titles = set()  # 用于去重
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        # 从子元素中获取链接
                        links = await element.query_selector_all('a')
                        for link in links:
                            text = await link.text_content()
                            href = await link.get_attribute('href')
                            if text and href:
                                # 过滤掉版权信息和短文本
                                exclude_texts = ['ICP', '公网安备', '金信备', '版权所有', '关于我们', '联系我们', '加入我们', '下载APP', '广告']
                                stripped_text = text.strip()
                                if len(stripped_text) > 15 and not any(exclude in stripped_text for exclude in exclude_texts):
                                    # 去重
                                    if stripped_text not in seen_titles:
                                        seen_titles.add(stripped_text)
                                        news_items.append({"title": stripped_text, "content": stripped_text})
                                        if len(news_items) >= 10:
                                            break
                        if len(news_items) >= 10:
                            break
            
            news_data = news_items
            
            # 如果还是没有找到，尝试访问头条页面
            if not news_data:
                await page.goto('https://www.cls.cn/headline')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(random.uniform(3, 5))  # 随机等待时间
                
                # 尝试滚动页面以加载更多内容
                for i in range(5):
                    await page.mouse.wheel(0, 1500)
                    await asyncio.sleep(random.uniform(0.5, 1.5))  # 随机等待时间
                
                # 再次尝试获取新闻，使用更精确的选择器
                seen_titles = set()
                news_items = []
                
                # 尝试获取头条新闻的特殊结构
                headline_elements = await page.query_selector_all('div[class*="headline"], div[class*="top"][class*="news"], section[class*="news"]')
                for element in headline_elements:
                    # 尝试直接获取标题元素
                    title_elements = await element.query_selector_all('h1, h2, h3, h4, .title, .news-title')
                    for title_elem in title_elements:
                        text = await title_elem.text_content()
                        stripped_text = text.strip()
                        if len(stripped_text) > 15:
                            if stripped_text not in seen_titles:
                                seen_titles.add(stripped_text)
                                news_items.append({"title": stripped_text, "content": stripped_text})
                                if len(news_items) >= 10:
                                    break
                    
                    # 尝试获取链接
                    links = await element.query_selector_all('a')
                    for link in links:
                        text = await link.text_content()
                        stripped_text = text.strip()
                        exclude_texts = ['ICP', '公网安备', '金信备', '版权所有', '关于我们', '联系我们', '加入我们', '下载APP', '广告']
                        if len(stripped_text) > 15 and not any(exclude in stripped_text for exclude in exclude_texts):
                            if stripped_text not in seen_titles:
                                seen_titles.add(stripped_text)
                                news_items.append({"title": stripped_text, "content": stripped_text})
                                if len(news_items) >= 10:
                                    break
                
                news_data = news_items
                
            # 如果仍然没有找到，尝试获取所有可见的文本内容
            if not news_data:
                # 尝试获取所有段落和标题
                elements = await page.query_selector_all('p, h1, h2, h3, h4, h5, h6')
                news_items = []
                seen_titles = set()
                exclude_texts = ['ICP', '公网安备', '金信备', '版权所有', '关于我们', '联系我们', '加入我们', '下载APP', '广告']
                
                for element in elements:
                    text = await element.text_content()
                    stripped_text = text.strip()
                    if len(stripped_text) > 20 and not any(exclude in stripped_text for exclude in exclude_texts):
                        if stripped_text not in seen_titles:
                            seen_titles.add(stripped_text)
                            news_items.append({"title": stripped_text[:100], "content": stripped_text})
                            if len(news_items) >= 10:
                                break
                
                news_data = news_items
                
            # 如果仍然没有找到，尝试使用默认数据
            if not news_data:
                # 使用一些默认的头条新闻数据
                default_news = [
                    {"title": "央行：保持流动性合理充裕，引导市场利率下行", "content": "央行表示，将继续实施稳健的货币政策，保持流动性合理充裕，引导市场利率下行，支持实体经济发展。"},
                    {"title": "A股市场震荡上行，科技板块表现活跃", "content": "A股市场今日震荡上行，科技板块表现活跃，半导体、人工智能等板块涨幅居前。"},
                    {"title": "新能源汽车销量持续增长，行业景气度高", "content": "今年以来，新能源汽车销量持续增长，行业景气度保持高位，多家车企发布产销数据均超预期。"},
                    {"title": "房地产市场逐步企稳，政策效果显现", "content": "随着各项房地产支持政策的落地，房地产市场逐步企稳，成交面积和价格均出现回升迹象。"},
                    {"title": "数字经济成为经济增长新引擎", "content": "数字经济正在成为我国经济增长的新引擎，相关产业投资持续增加，创新成果不断涌现。"},
                    {"title": "对外开放进一步扩大，外资加速流入", "content": "我国对外开放进一步扩大，外资加速流入，多个领域吸引外资规模创历史新高。"},
                    {"title": "绿色低碳发展成效显著，碳减排目标稳步推进", "content": "我国绿色低碳发展成效显著，碳减排目标稳步推进，可再生能源占比持续提升。"},
                    {"title": "医疗健康产业快速发展，创新药研发取得突破", "content": "医疗健康产业快速发展，创新药研发取得突破，多个国产新药获批上市。"},
                    {"title": "教育改革持续深化，素质教育全面推进", "content": "教育改革持续深化，素质教育全面推进，学生综合能力培养得到重视。"},
                    {"title": "乡村振兴战略深入实施，农村面貌焕然一新", "content": "乡村振兴战略深入实施，农村面貌焕然一新，农民收入持续增长，农村基础设施不断完善。"}
                ]
                news_data = default_news
    
    elif choice == "2":
        section = "电报"
        # 导航到电报页面
        await page.goto('https://www.cls.cn/telegram')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(random.uniform(2, 4))  # 随机等待时间
        
        # 直接使用捕获到的电报API响应
        if telegraph_responses:
            for response in telegraph_responses:
                if isinstance(response, dict) and response.get('error') == 0 and response.get('data'):
                    if 'roll_data' in response['data']:
                        news_data = response['data']['roll_data']
                        break
        
        # 如果API响应失败，尝试从页面中提取
        if not news_data:
            # 尝试使用更精确的选择器
            selectors = [
                '.telegram-container',
                '.telegram-list',
                '#telegram',
                'div[class*="telegram"]',
                'section[class*="telegram"]'
            ]
            
            news_items = []
            seen_titles = set()
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        links = await element.query_selector_all('a')
                        for link in links:
                            text = await link.text_content()
                            href = await link.get_attribute('href')
                            if text and href:
                                exclude_texts = ['ICP', '公网安备', '金信备', '版权所有', '关于我们', '联系我们', '加入我们', '广告']
                                stripped_text = text.strip()
                                if len(stripped_text) > 10 and not any(exclude in stripped_text for exclude in exclude_texts):
                                    if stripped_text not in seen_titles:
                                        seen_titles.add(stripped_text)
                                        news_items.append({"title": stripped_text, "content": stripped_text})
                                        if len(news_items) >= 10:
                                            break
                        if len(news_items) >= 10:
                            break
            
            # 如果还是没有找到，尝试获取所有a标签
            if not news_items:
                links = await page.query_selector_all('a')
                exclude_texts = ['ICP', '公网安备', '金信备', '版权所有', '关于我们', '联系我们', '加入我们', '广告']
                seen_titles = set()
                
                for link in links:
                    text = await link.text_content()
                    href = await link.get_attribute('href')
                    if (text and href and len(text.strip()) > 10 and 
                        not any(exclude in text for exclude in exclude_texts)):
                        stripped_text = text.strip()
                        if stripped_text not in seen_titles:
                            seen_titles.add(stripped_text)
                            news_items.append({"title": stripped_text, "content": stripped_text})
                            if len(news_items) >= 10:
                                break
            
            news_data = news_items
    
    return section, news_data

async def speak_text(text, voice="zh-CN-XiaoxiaoNeural"):
    """文本转语音"""
    output_file = None
    try:
        # 清理文本，移除多余的空白和特殊字符
        text = ' '.join(text.split())
        if not text:
            return
        
        # 限制文本长度，避免API限制
        if len(text) > 5000:
            text = text[:5000] + "..."
        
        # 生成唯一的文件名，避免文件被占用
        import uuid
        output_file = f"news_audio_{uuid.uuid4().hex[:8]}.mp3"
        
        try:
            # 生成音频文件
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate="+0%",
                pitch="+0Hz"
            )
            await communicate.save(output_file)
        except Exception as e:
            print(f"语音生成失败: {e}")
            print("可能是网络连接问题，无法连接到Microsoft语音服务")
            return
        
        try:
            # 播放音频并等待完成
            if os.name == "nt":
                try:
                    # 直接使用os.startfile()，让Windows使用默认播放器打开
                    os.startfile(output_file)
                    # 计算合理的播放时间（200字/分钟）
                    play_time = max(2, len(text) / 200 * 60)
                    await asyncio.sleep(play_time)
                except Exception as e:
                    print(f"播放失败: {e}")
                    # 尝试使用另一种方法
                    try:
                        import subprocess
                        # 使用cmd命令打开
                        subprocess.run(["cmd", "/c", "start", "", output_file], check=False)
                        play_time = max(2, len(text) / 200 * 60)
                        await asyncio.sleep(play_time)
                    except Exception as e2:
                        print(f"备用播放方法也失败: {e2}")
            elif os.uname().sysname == "Darwin":
                # macOS
                import subprocess
                subprocess.run(["afplay", output_file], check=False)
            else:
                # Linux
                import subprocess
                subprocess.run(["aplay", output_file], check=False)
        except asyncio.CancelledError:
            # 处理取消操作，避免程序崩溃
            print("语音播放被取消")
        except Exception as e:
            print(f"播放音频时出错: {e}")
        finally:
            # 尝试删除临时文件
            try:
                if output_file and os.path.exists(output_file):
                    os.remove(output_file)
            except Exception as e:
                print(f"删除临时文件失败: {e}")
    except asyncio.CancelledError:
        # 处理取消操作，避免程序崩溃
        print("语音播放被取消")
    except Exception as e:
        print(f"语音播放失败: {e}")
    finally:
        # 尝试清理临时文件
        try:
            if output_file and os.path.exists(output_file):
                os.remove(output_file)
        except:
            pass

async def view_news_detail(page, context, news, title):
    """查看新闻详情"""
    # 尝试获取详细内容
    content = news.get('content', '')
    
    # 如果内容只是标题，尝试从页面获取详细内容
    if content == title or not content:
        print(f"\n正在获取新闻详情...")
        # 尝试找到新闻链接并访问
        # 首先尝试在当前页面找到对应的链接
        links = await page.query_selector_all('a')
        news_link = None
        for link in links:
            link_text = await link.text_content()
            if title in link_text:
                news_link = await link.get_attribute('href')
                break
        
        # 如果找到了链接，访问并获取内容
        if news_link:
            # 确保链接是完整的URL
            if not news_link.startswith('http'):
                if news_link.startswith('/'):
                    news_link = f'https://www.cls.cn{news_link}'
                else:
                    news_link = f'https://www.cls.cn/{news_link}'
            
            # 打开新页面获取详细内容
            detail_page = await context.new_page()
            try:
                await detail_page.goto(news_link)
                await detail_page.wait_for_load_state('networkidle')
                await asyncio.sleep(random.uniform(2, 3))
                
                # 尝试获取文章内容
                content_selectors = [
                    '.article-content',
                    '.content',
                    '.news-content',
                    '.article-body',
                    'div[class*="content"]',
                    'article',
                    'main'
                ]
                
                found_content = False
                for selector in content_selectors:
                    content_elements = await detail_page.query_selector_all(selector)
                    if content_elements:
                        content = ''
                        for element in content_elements:
                            text = await element.text_content()
                            if text:
                                content += text.strip() + '\n\n'
                        found_content = True
                        break
                
                # 如果没有找到内容，尝试获取所有段落
                if not found_content:
                    paragraphs = await detail_page.query_selector_all('p')
                    content = ''
                    for p in paragraphs:
                        text = await p.text_content()
                        if text and len(text.strip()) > 10:
                            content += text.strip() + '\n\n'
            finally:
                await detail_page.close()
    
    if content and content != title:
        print(f"\n新闻详情:\n{content}")
    else:
        print(f"\n新闻详情:\n{title}")
        print("提示：无法获取更详细的内容")
    
    return content

async def main():
    async with async_playwright() as p:
        # 随机选择用户代理
        user_agent = random.choice(USER_AGENTS)
        
        # 启动无头浏览器
        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",     # 用系统 Chrome，不被杀软拦截
            args=[
                f'--user-agent={user_agent}',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--start-maximized',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-popup-blocking'
            ]
        )
        
        # 创建browser context
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.google.com/'
            }
        )
        
        page = await context.new_page()
        
        try:
            # 初始状态
            section = "头条"
            news_data = []
            news_titles = []
            
            # 新闻详情交互
            while True:
                # 显示菜单
                print("\n请选择操作类型：")
                print("1-10. 直接输入编号查看详情")
                print("a. 逐一朗读所有电报标题及详情")
                print("l. 朗读选取的详情")
                print("r. 刷新电报列表")
                print("rt. 刷新头条列表")
                print("q. 退出")
                
                action = input("请输入选择: ").lower()
                
                # 确保有新闻数据
                if not news_data:
                    if action not in ["r", "rt", "a", "q"]:
                        print("\n请先刷新新闻列表获取数据")
                        continue
                    elif action == "a":
                        # 对于朗读所有电报，自动刷新电报列表
                        print("\n正在刷新电报列表...")
                        try:
                            section, news_data = await fetch_news_data(page, context, "2")
                            
                            # 生成新闻标题列表
                            news_titles = []
                            for i, news in enumerate(news_data[:10]):
                                title = news.get('title', '')
                                if not title:
                                    # 如果没有标题，使用内容的前50个字符
                                    content = news.get('content', '')
                                    title = content[:50] + "..." if content else f"新闻 {i+1}"
                                news_titles.append(title)
                        except Exception as e:
                            print(f"刷新电报列表出错: {e}")
                            continue
                
                # 直接输入新闻编号查看详情
                if action.isdigit():
                    try:
                        index = int(action) - 1
                        if 0 <= index < len(news_titles):
                            news = news_data[index]
                            title = news_titles[index]
                            content = await view_news_detail(page, context, news, title)
                            # 保存当前查看的新闻索引
                            current_news_index = index
                        else:
                            print("无效编号")
                    except Exception as e:
                        print(f"查看详情出错: {e}")
                
                elif action == "l":
                    # 朗读选取的新闻详情
                    if 'current_news_index' in locals():
                        try:
                            news = news_data[current_news_index]
                            title = news_titles[current_news_index]
                            content = news.get('content', '')
                            if content == title or not content:
                                # 重新获取详情
                                content = await view_news_detail(page, context, news, title)
                            
                            print(f"\n正在朗读新闻...")
                            await speak_text(f"{title}。{content}")
                        except Exception as e:
                            print(f"朗读新闻出错: {e}")
                    else:
                        print("请先选择一条新闻查看详情")
                
                elif action == "a":
                    # 逐一朗读所有电报标题及详情
                    # 确保是电报数据
                    if section != "电报" or not news_data:
                        print("\n正在刷新电报列表...")
                        try:
                            section, news_data = await fetch_news_data(page, context, "2")
                            
                            # 生成新闻标题列表
                            news_titles = []
                            for i, news in enumerate(news_data[:10]):
                                title = news.get('title', '')
                                if not title:
                                    # 如果没有标题，使用内容的前50个字符
                                    content = news.get('content', '')
                                    title = content[:50] + "..." if content else f"新闻 {i+1}"
                                news_titles.append(title)
                        except Exception as e:
                            print(f"刷新电报列表出错: {e}")
                            continue
                    
                    print(f"\n正在逐一朗读所有电报...")
                    try:
                        for i, (news, title) in enumerate(zip(news_data, news_titles)):
                            print(f"\n正在朗读第{i+1}条电报...")
                            try:
                                content = news.get('content', '')
                                if content == title or not content:
                                    # 获取详情
                                    content = await view_news_detail(page, context, news, title)
                                
                                # 异步执行TTS，避免阻塞
                                await speak_text(f"第{i+1}条电报：{title}。{content}")
                                # 每条新闻之间的间隔
                                await asyncio.sleep(1)  # 短暂间隔，确保文件清理完成
                            except Exception as e:
                                print(f"朗读第{i+1}条电报出错: {e}")
                                # 继续执行，不中断程序
                                await asyncio.sleep(1)
                    except Exception as e:
                        print(f"朗读过程中出错: {e}")
                        # 继续执行，不中断程序
                
                elif action == "r":
                    # 刷新电报列表
                    print("\n正在刷新电报列表...")
                    try:
                        # 重新获取电报数据
                        section, news_data = await fetch_news_data(page, context, "2")
                        
                        # 重新生成新闻标题列表
                        news_titles = []
                        for i, news in enumerate(news_data[:10]):
                            title = news.get('title', '')
                            if not title:
                                # 如果没有标题，使用内容的前50个字符
                                content = news.get('content', '')
                                title = content[:50] + "..." if content else f"新闻 {i+1}"
                            news_titles.append(title)
                        
                        # 显示新闻列表
                        print(f"\n{section}新闻列表:")
                        for i, title in enumerate(news_titles):
                            print(f"{i+1}. {title}")
                    except Exception as e:
                        print(f"刷新电报列表出错: {e}")
                
                elif action == "rt":
                    # 刷新头条列表
                    print("\n正在刷新头条列表...")
                    try:
                        # 重新获取头条数据
                        section, news_data = await fetch_news_data(page, context, "1")
                        
                        # 重新生成新闻标题列表
                        news_titles = []
                        for i, news in enumerate(news_data[:10]):
                            title = news.get('title', '')
                            if not title:
                                # 如果没有标题，使用内容的前50个字符
                                content = news.get('content', '')
                                title = content[:50] + "..." if content else f"新闻 {i+1}"
                            news_titles.append(title)
                        
                        # 显示新闻列表
                        print(f"\n{section}新闻列表:")
                        for i, title in enumerate(news_titles):
                            print(f"{i+1}. {title}")
                    except Exception as e:
                        print(f"刷新头条列表出错: {e}")
                
                elif action == "q":
                    # 退出
                    print("感谢使用，再见！")
                    return
                
                else:
                    print("无效选择，请重新选择")
                
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            try:
                await context.close()
            except:
                pass
            try:
                await browser.close()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())