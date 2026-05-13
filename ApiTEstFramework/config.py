class Config:
    """每个环境都有一样的公共配置"""
    version = "v1.0"
    appId = "dpm"
    # 定义全局请求头
    global_headers = {
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Fetch-User": "?1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.8,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Sec-Fetch-Dest": "document"
    }

class uat_env(Config):
    """UAT环境"""
    BASE_URL = 'dpmuat.midea.com'
    AUTH_URL = 'signinuat.midea.com'
    USERNAME = 'shenjh40'
    PASSWORD = 'RwWkuuw8i8XDoPNyCzBXLQ=='

# 环境关系映射，方便切换多环境配置
env = {
    "uat": uat_env
}
