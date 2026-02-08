# 尝试从langchain_text_splitters导入
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("Found RecursiveCharacterTextSplitter in langchain_text_splitters")
    
    # 测试创建实例
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", ";", "；", "，", ",", " "]
    )
    print("Successfully created RecursiveCharacterTextSplitter instance")
except ImportError as e:
    print(f"Failed to import from langchain_text_splitters: {e}")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter as RCTS
    print("Found RCTS in langchain_text_splitters")
except ImportError as e:
    print(f"Failed to import RCTS from langchain_text_splitters: {e}")
