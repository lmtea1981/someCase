"""
===================================
@Author: Djl
@Date: 2025/12/30 16:08
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient


class McpCall:
    def __init__(self):
        # 你的 API Key
        self.AMAP_API_KEY = 
        # 初始化 MCP 客户端
        self.client = MultiServerMCPClient(
            {
                'amap_mcp': {
                    'transport': 'stdio',
                    "command": "uvx",
                    "args": ["amap-mcp-server"],
                    "env": {"AMAP_MAPS_API_KEY": self.AMAP_API_KEY}
                },
            }
        )

    async def get_mytools(self):
        # 获取所有可用工具
        tools = await self.client.get_tools()
        print("可用工具：")
        for tool in tools:
            print(f"工具名: {tool.name}, 描述: {tool.description}")
        return tools

    async def get_weather(self):
        tools = await self.get_mytools()
        # 找到天气工具
        weather_tool = next(t for t in tools if t.name == "maps_weather")
        # 调用工具
        result = await weather_tool.ainvoke({"city": "广州"})

        print("\n调用结果：")
        print(result)

    async def get_roadPlan(self):
        tools = await self.get_mytools()
        # 找到公交路线规划
        # route_tool = next(t for t in tools if t.name == "maps_bicycling_by_address")
        # route_tool = next(t for t in tools if t.name == "maps_direction_driving_by_address")
        route_tool = next(t for t in tools if t.name == "maps_direction_transit_integrated_by_address")

        # 调用工具
        result = await route_tool.ainvoke({
            "origin_address": "北京市朝阳区阜通东大街6号",
            "destination_address": "北京市海淀区上地十街10号",
            "origin_city": "北京",
            "destination_city": "北京"
        })

        print(f"====4444{result}")

        # 解析返回
        text_data = result[0]['text']
        data = json.loads(text_data)
        # print(f"===格式是：{type(data)}")

        if "error" in data:
            print("❌ 路线规划失败：", data["error"])
        else:
            if isinstance(data, dict):
                if "data" in data:
                    # 提取基本信息
                    origin_addr = data['addresses']['origin']['address']
                    origin_coords = data['addresses']['origin']['coordinates']
                    dest_addr = data['addresses']['destination']['address']
                    dest_coords = data['addresses']['destination']['coordinates']

                    total_distance = data['data']['paths'][0]['distance']
                    total_duration = data['data']['paths'][0]['duration']

                    total_duration = int(total_duration)
                    if total_duration > 60:
                        total_duration = str(round(total_duration / 60, 2)) + "分钟"
                    else:
                        total_duration = str(total_duration) + "秒"

                    # 打印概览
                    print(f"起点：{origin_addr} ({origin_coords})")
                    print(f"终点：{dest_addr} ({dest_coords})")
                    print(f"总距离：{total_distance}米")
                    print(f"总时间：{total_duration}")

                    # 打印每一步导航
                    print("\n路线导航：")
                    for i, step in enumerate(data['data']['paths'][0]['steps'], 1):
                        instruction = step['instruction']
                        road = step['road'] if step['road'] else "无名道路"
                        print(f"{i}. {instruction} (road: {road})")
                elif "route" in data:
                    # 提取基本信息
                    origin_addr = data['addresses']['origin']['address']
                    origin_coords = data['addresses']['origin']['coordinates']
                    dest_addr = data['addresses']['destination']['address']
                    dest_coords = data['addresses']['destination']['coordinates']

                    total_distance = data['route']['paths'][0]['distance']
                    total_duration = data['route']['paths'][0]['duration']

                    total_duration = int(total_duration)
                    if total_duration > 60:
                        total_duration = str(round(total_duration / 60, 2)) + "分钟"
                    else:
                        total_duration = str(total_duration) + "秒"

                    # 打印概览
                    print(f"起点：{origin_addr} ({origin_coords})")
                    print(f"终点：{dest_addr} ({dest_coords})")
                    print(f"总距离：{total_distance}米")
                    print(f"总时间：{total_duration}")

                    # 打印每一步导航
                    print("\n路线导航：")
                    if "data" in data:
                        for i, step in enumerate(data['data']['paths'][0]['steps'], 1):
                            instruction = step['instruction']
                            road = step['road'] if step['road'] else "无名道路"
                            print(f"{i}. {instruction} (road: {road})")
                    elif "route" in data:
                        for i, step in enumerate(data['route']['paths'][0]['steps'], 1):
                            instruction = step['instruction']
                            road = step['road'] if step['road'] else "无名道路"
                            print(f"{i}. {instruction} (road: {road})")
            else:
                print("📍 返回单条路线：")
                print(f"   距离：{data.get('distance')} 米")
                print(f"   预计时间：{data.get('duration')} 秒")

    async def get_around_search(self, addr, range):
        tools = await self.get_mytools()
        # 找到天气工具
        get_geo = next(t for t in tools if t.name == "maps_geo")
        result = await get_geo.ainvoke({
            "address": addr
        })
        print("\n调用结果：")
        print(result)
        # 解析返回
        text_data = result[0]['text']
        data = json.loads(text_data)

        location = data['return'][0]['location']
        print(f"===location: {location}")

        # 00
        around_search = next(t for t in tools if t.name == "maps_around_search")
        # 调用工具
        # result = await weather_tool.ainvoke({"address": "广州工银大厦"})
        result = await around_search.ainvoke({
            "location": location,
            "radius": range,
        })

        print("\n调用结果：")
        print(result)
        # 解析返回
        text_data = result[0]['text']
        data = json.loads(text_data)
        buildings = data['pois']
        for b in buildings:
            print(f"建筑：{b['name']}\n地址：{b['address']}\n")

    async def get_keyword_search(self):
        tools = await self.get_mytools()
        # 找到天气工具
        # weather_tool = next(t for t in tools if t.name == "maps_geo")
        # weather_tool = next(t for t in tools if t.name == "maps_around_search")
        weather_tool = next(t for t in tools if t.name == "maps_text_search")
        # 调用工具
        # result = await weather_tool.ainvoke({"address": "广州工银大厦"})
        result = await weather_tool.ainvoke({
            # "location": "113.286255,23.113937",
            # "radius": "500",
            "keywords": "工银大厦",
            "city": "广州"
        })

        print("\n调用结果：")
        print(result)


if __name__ == "__main__":
    addr = input("请输入查询地址：")
    range = input("查询多少米范围：")
    a = McpCall()
    # asyncio.run(a.get_weather())
    # asyncio.run(a.get_roadPlan())
    # asyncio.run(a.get_around_search())
    asyncio.run(a.get_around_search(addr, range))


