from tools.browser_tools import BrowserTool

# 创建工具实例
browser_tool = BrowserTool()

# 直接调用工具，测试实际返回结果
url = "https://thehackernews.com/"
result = browser_tool._run(url)

print("=== BrowserTool实际返回结果 ===")
print(result)
print("\n=== 结果类型 ===")
print(type(result))
