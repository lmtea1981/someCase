import pkgutil
import langchain

print("LangChain modules:")
for _, modname, _ in pkgutil.walk_packages(langchain.__path__):
    print(modname)

# 尝试查找RecursiveCharacterTextSplitter
print("\nTrying to find RecursiveCharacterTextSplitter...")

# 尝试所有可能的路径
try_paths = [
    'langchain.text_splitter',
    'langchain_core.text_splitter',
    'langchain_community.text_splitter',
    'langchain.document_transformers',
    'langchain_core.document_transformers',
    'langchain_community.document_transformers',
    'langchain.text_splitter',
    'langchain.text_splitter',
    'langchain.text_splitter'
]

for path in try_paths:
    try:
        module = __import__(path, fromlist=['RecursiveCharacterTextSplitter'])
        if hasattr(module, 'RecursiveCharacterTextSplitter'):
            print(f"Found in {path}")
            break
    except ImportError:
        continue

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain.text_splitter")
except ImportError:
    pass

try:
    from langchain_core.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain_core.text_splitter")
except ImportError:
    pass

try:
    from langchain_community.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain_community.text_splitter")
except ImportError:
    pass

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain.text_splitter")
except ImportError:
    pass

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("Found in langchain.text_splitter")
except ImportError:
    pass

# 尝试直接搜索所有已安装的包
print("\nTrying to search all installed packages...")
import subprocess
result = subprocess.run(
    ["python", "-c", "import pkgutil; import sys; [print(pkg) for _, pkg, _ in pkgutil.iter_modules(sys.path)]"],
    capture_output=True,
    text=True
)

# 打印所有包含langchain的包
print("\nAll langchain-related packages:")
for line in result.stdout.splitlines():
    if "langchain" in line:
        print(line)
