# 模型配置
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "qwen3:latest"
EMBEDDING_MODEL = "qwen3:latest"
KEEP_ALIVE = 300  # 秒

# 文本处理参数
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
SEPARATORS = ["\n\n", "\n", "。", "！", "？", ".", "!", "?", ";", "；", "，", ",", " "]
MAX_TEXT_LENGTH = 2000
BATCH_SIZE = 10

# 测试设计方法列表
TEST_METHODS = [
    "等价类划分法",
    "边界值分析法",
    "异常分析法",
    "场景法",
    "因果图法",
    "正交试验法",
    "判定表法"
]

# 路径配置
CASE_LIBRARY_PATH = "./testdata_1.xlsx"
DATABASE_PATH = "sqlite:///test_cases.db"
VECTOR_STORE_PATH = "./vector_store"

# 检索配置
TOP_K = 10
SIMILARITY_THRESHOLD = 0.5
