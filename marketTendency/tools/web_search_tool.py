from langchain.tools import tool
from typing import List, Dict
from langchain_community.tools.tavily_search import TavilySearchResults
from config import TOOLS_CONFIG

@tool
def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    搜索网络资讯，获取与查询相关的信息
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量限制，默认为5
    
    Returns:
        结构化的搜索结果列表，每个结果包含标题、链接、摘要等信息
    """
    try:
        results = []
        
        # 从配置中获取Tavily API密钥
        tavily_api_key = TOOLS_CONFIG.get("tavily_api_key", "")
        
        # 使用Tavily搜索
        tavily_search = TavilySearchResults(
            api_key=tavily_api_key,
            max_results=max_results
        )
        search_results = tavily_search.run(query)
        
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", ""),
                "source": "tavily"
            })
        
        # 如果搜索结果为空，返回默认结果
        if not results:
            results.append({
                "title": "No results found",
                "url": "",
                "snippet": f"No results found for query: {query}",
                "source": "tavily"
            })
        
        return results
    except Exception as e:
        return [{"error": f"搜索失败: {str(e)}"}]
