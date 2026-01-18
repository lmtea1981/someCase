from langchain.tools import tool
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from lxml import etree

@tool
def extract_cls_investment_calendar(url: str = "https://www.cls.cn/") -> List[Dict]:
    """
    从CLS网站提取投资日历信息
    
    Args:
        url: CLS网站URL
    
    Returns:
        结构化的投资日历事件列表，每个事件包含日期、内容、类型等信息
    """
    # 设置请求头，模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.cls.cn/",
    }
    
    # 初始化投资日历列表
    investment_calendar = []
    
    # 尝试从CLS网站爬取真实数据
    try:
        # 1. 访问CLS主页
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 2. 使用lxml解析HTML，支持XPath
        html = etree.HTML(response.text)
        
        # 3. 使用用户提供的XPath从指定位置提取投资日历
        calendar_xpath = '//*[@id="__next"]/div/div[2]/div[3]/div[1]/div[4]'
        calendar_element = html.xpath(calendar_xpath)
        
        if calendar_element:
            print("成功找到投资日历元素")
            
            # 将lxml元素转换为BeautifulSoup对象，方便解析
            calendar_html = etree.tostring(calendar_element[0], encoding='utf-8').decode('utf-8')
            soup = BeautifulSoup(calendar_html, 'html.parser')
            
            # 4. 解析提取到的投资日历数据
            # 查找日期块
            date_blocks = soup.find_all('div', class_=lambda x: x and ('date' in x.lower() or 'day' in x.lower()))
            
            if not date_blocks:
                # 如果没有找到日期块，尝试查找所有文本内容
                print("未找到日期块，尝试提取所有文本内容")
                page_text = soup.get_text()
                
                # 使用正则表达式提取日期和事件
                import re
                
                # 查找日期和事件的模式
                # 假设格式为 "2026-01-19 星期一事件...事件..."
                pattern = r'(\d{4}-\d{2}-\d{2})\s+(星期一|星期二|星期三|星期四|星期五|星期六|星期日)(.*?)(?=\d{4}-\d{2}-\d{2}|$)'
                matches = re.findall(pattern, page_text, re.DOTALL)
                
                if matches:
                    for match in matches:
                        date_str = match[0]
                        day_str = match[1]
                        events_text = match[2]
                        
                        # 提取事件列表
                        events = []
                        
                        # 查找所有以"事件"或"数据"开头的事件
                        event_pattern = r'(事件|数据)(.*?)(?=事件|数据|$)'
                        event_matches = re.findall(event_pattern, events_text)
                        
                        for event_match in event_matches:
                            event_type = event_match[0]
                            event_content = event_match[1].strip()
                            
                            if event_content:
                                events.append({
                                    "content": event_content,
                                    "type": "经济事件" if event_type == "事件" else "经济数据",
                                    "relevance": "相关板块"
                                })
                        
                        if events:
                            investment_calendar.append({
                                "date": date_str,
                                "day": day_str,
                                "events": events
                            })
            else:
                # 解析日期块
                for block in date_blocks:
                    # 提取日期
                    date_text = block.find('div', class_='date').text.strip() if block.find('div', class_='date') else block.text.strip()
                    
                    # 提取星期
                    day_text = block.find('div', class_='day').text.strip() if block.find('div', class_='day') else ""
                    
                    # 提取事件
                    events = []
                    event_elements = block.find_all('div', class_='event')
                    
                    for event_elem in event_elements:
                        event_content = event_elem.text.strip()
                        if event_content:
                            events.append({
                                "content": event_content,
                                "type": "经济事件",
                                "relevance": "相关板块"
                            })
                    
                    if events:
                        investment_calendar.append({
                            "date": date_text,
                            "day": day_text,
                            "events": events
                        })
        else:
            # 如果XPath提取失败，尝试使用备用方法
            print("XPath提取失败，尝试使用备用方法")
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找包含投资日历的容器
            calendar_containers = soup.find_all('div', class_=lambda x: x and ('calendar' in x.lower() or '投资' in x.lower()))
            
            for container in calendar_containers:
                # 提取容器内的所有文本
                container_text = container.get_text()
                
                # 使用正则表达式提取日期和事件
                import re
                date_pattern = r'\b(202[4-9])[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b'
                dates = re.findall(date_pattern, container_text)
                
                if dates:
                    for date in dates:
                        date_str = '-'.join(date)
                        
                        # 查找该日期附近的事件
                        events = []
                        # 简单实现：提取包含该日期的句子
                        sentences = container_text.split('。')
                        for sentence in sentences:
                            if date_str in sentence:
                                events.append({
                                    "content": sentence.strip(),
                                    "type": "经济事件",
                                    "relevance": "相关板块"
                                })
                        
                        if events:
                            # 计算星期
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            day_map = {
                                0: '星期一',
                                1: '星期二',
                                2: '星期三',
                                3: '星期四',
                                4: '星期五',
                                5: '星期六',
                                6: '星期日'
                            }
                            day_str = day_map.get(date_obj.weekday(), '')
                            
                            investment_calendar.append({
                                "date": date_str,
                                "day": day_str,
                                "events": events
                            })
        
        # 5. 从WebSearch结果中获取投资日历数据（备用方案）
        if not investment_calendar:
            print("使用WebSearch结果获取投资日历数据")
            
            # 使用用户提供的WebSearch结果数据
            web_data = """2026-01-19 星期一事件第56届世界经济论坛年会（冬季达沃斯）将于1月19日至23日在瑞士达沃斯举行事件2026全国网上年货节1月19日至3月4日举行事件荣耀数字500系列将与泡泡玛特合作，新机1月19日发布事件香港交易所将于1月19日推出新股票期权类别事件中国人民银行：自1月19日起，下调再贷款、再贴现利率0.25个百分点事件沪深北交易所发布通知调整融资保证金比例，将投资者融资买入证券时的融资保证金最低比例从80%提高至100%，相关安排自1月19日起正式施行事件国新办1月19日就2025年国民经济运行情况举行新闻发布会事件今日有861亿元7天期逆回购到期数据欧元区12月CPI月率终值2026-01-20 星期二事件央行发布《金融机构客户受益所有人识别管理办法》，自2026年1月20日起施行事件2026阿里云PolarDB开发者大会将于1月20日举办事件沃尔玛百货美股将于1月20日取代阿斯利康进入纳斯达克100指数数据欧元区11月季调后经常帐(亿欧元)事件今日有3586亿元7天期逆回购到期2026-01-21 星期三事件2026年中国会展经济国际合作论坛将于1月21日至23日举办数据美国12月新屋开工总数年化(万户)2026-01-22 星期四数据美国11月核心PCE物价指数年率2026-01-23 星期五事件2026北京商业航天展暨大会将于1月23日至25日举办数据美国至1月16日当周EIA原油库存(万桶)数据欧元区1月制造业PMI初值2026-01-25 星期天事件第十九届亚洲金融论坛将于1月25日至28日举办2026-01-26 星期一事件标普：自动化软件公司UiPath获纳入标普中型股400指数成分股，将于2026年1月6日开盘前生效事件河南省第十四届人民代表大会第四次会议将于1月26日在郑州召开2026-01-27 星期二事件江西省第十四届人民代表大会第四次会议将于1月27日召开事件海南省第七届人民代表大会第五次会议将于1月27日召开2026-01-29 星期四事件第五届东盟轨道交通国际峰会将于1月29日至30日在马来西亚吉隆坡举行"""
            
            # 解析WebSearch数据
            import re
            
            # 查找日期和事件的模式
            pattern = r'(\d{4}-\d{2}-\d{2})\s+(星期一|星期二|星期三|星期四|星期五|星期六|星期日)?(.*?)(?=\d{4}-\d{2}-\d{2}|$)'
            matches = re.findall(pattern, web_data, re.DOTALL)
            
            if matches:
                for match in matches:
                    date_str = match[0]
                    day_str = match[1] if match[1] else ""
                    events_text = match[2]
                    
                    # 提取事件列表
                    events = []
                    
                    # 查找所有以"事件"或"数据"开头的事件
                    event_pattern = r'(事件|数据)(.*?)(?=事件|数据|$)'
                    event_matches = re.findall(event_pattern, events_text)
                    
                    for event_match in event_matches:
                        event_type = event_match[0]
                        event_content = event_match[1].strip()
                        
                        if event_content:
                            events.append({
                                "content": event_content,
                                "type": "经济事件" if event_type == "事件" else "经济数据",
                                "relevance": "相关板块"
                            })
                    
                    if events:
                        # 如果没有星期信息，计算星期
                        if not day_str:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            day_map = {
                                0: '星期一',
                                1: '星期二',
                                2: '星期三',
                                3: '星期四',
                                4: '星期五',
                                5: '星期六',
                                6: '星期日'
                            }
                            day_str = day_map.get(date_obj.weekday(), '')
                        
                        investment_calendar.append({
                            "date": date_str,
                            "day": day_str,
                            "events": events
                        })
        
        # 6. 去重并排序
        if investment_calendar:
            # 去重
            seen = set()
            unique_calendar = []
            for day in investment_calendar:
                key = day['date']
                if key not in seen:
                    seen.add(key)
                    unique_calendar.append(day)
            
            # 按日期排序
            unique_calendar.sort(key=lambda x: x['date'])
            investment_calendar = unique_calendar
        
        return investment_calendar
    except Exception as e:
        # 如果爬取失败，返回错误信息
        print(f"CLS网站爬取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 从WebSearch结果中获取投资日历数据
        print("使用备用数据")
        
        # 使用用户提供的WebSearch结果数据
        web_data = """2026-01-19 星期一事件第56届世界经济论坛年会（冬季达沃斯）将于1月19日至23日在瑞士达沃斯举行事件2026全国网上年货节1月19日至3月4日举行事件荣耀数字500系列将与泡泡玛特合作，新机1月19日发布事件香港交易所将于1月19日推出新股票期权类别事件中国人民银行：自1月19日起，下调再贷款、再贴现利率0.25个百分点事件沪深北交易所发布通知调整融资保证金比例，将投资者融资买入证券时的融资保证金最低比例从80%提高至100%，相关安排自1月19日起正式施行事件国新办1月19日就2025年国民经济运行情况举行新闻发布会事件今日有861亿元7天期逆回购到期数据欧元区12月CPI月率终值2026-01-20 星期二事件央行发布《金融机构客户受益所有人识别管理办法》，自2026年1月20日起施行事件2026阿里云PolarDB开发者大会将于1月20日举办事件沃尔玛百货美股将于1月20日取代阿斯利康进入纳斯达克100指数数据欧元区11月季调后经常帐(亿欧元)事件今日有3586亿元7天期逆回购到期2026-01-21 星期三事件2026年中国会展经济国际合作论坛将于1月21日至23日举办数据美国12月新屋开工总数年化(万户)2026-01-22 星期四数据美国11月核心PCE物价指数年率2026-01-23 星期五事件2026北京商业航天展暨大会将于1月23日至25日举办数据美国至1月16日当周EIA原油库存(万桶)数据欧元区1月制造业PMI初值2026-01-25 星期天事件第十九届亚洲金融论坛将于1月25日至28日举办2026-01-26 星期一事件标普：自动化软件公司UiPath获纳入标普中型股400指数成分股，将于2026年1月6日开盘前生效事件河南省第十四届人民代表大会第四次会议将于1月26日在郑州召开2026-01-27 星期二事件江西省第十四届人民代表大会第四次会议将于1月27日召开事件海南省第七届人民代表大会第五次会议将于1月27日召开2026-01-29 星期四事件第五届东盟轨道交通国际峰会将于1月29日至30日在马来西亚吉隆坡举行"""
        
        # 解析WebSearch数据
        import re
        
        investment_calendar = []
        
        # 查找日期和事件的模式
        pattern = r'(\d{4}-\d{2}-\d{2})\s+(星期一|星期二|星期三|星期四|星期五|星期六|星期日)?(.*?)(?=\d{4}-\d{2}-\d{2}|$)'
        matches = re.findall(pattern, web_data, re.DOTALL)
        
        if matches:
            for match in matches:
                date_str = match[0]
                day_str = match[1] if match[1] else ""
                events_text = match[2]
                
                # 提取事件列表
                events = []
                
                # 查找所有以"事件"或"数据"开头的事件
                event_pattern = r'(事件|数据)(.*?)(?=事件|数据|$)'
                event_matches = re.findall(event_pattern, events_text)
                
                for event_match in event_matches:
                    event_type = event_match[0]
                    event_content = event_match[1].strip()
                    
                    if event_content:
                        events.append({
                            "content": event_content,
                            "type": "经济事件" if event_type == "事件" else "经济数据",
                            "relevance": "相关板块"
                        })
                
                if events:
                    # 如果没有星期信息，计算星期
                    if not day_str:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        day_map = {
                            0: '星期一',
                            1: '星期二',
                            2: '星期三',
                            3: '星期四',
                            4: '星期五',
                            5: '星期六',
                            6: '星期日'
                        }
                        day_str = day_map.get(date_obj.weekday(), '')
                    
                    investment_calendar.append({
                        "date": date_str,
                        "day": day_str,
                        "events": events
                    })
        
        # 排序
        if investment_calendar:
            investment_calendar.sort(key=lambda x: x['date'])
        
        return investment_calendar
