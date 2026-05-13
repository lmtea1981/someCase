# conftest.py
import pytest
import requests
from typing import Dict, Any

@pytest.fixture(scope="session")
def shared_session():
    """创建全局共享的 requests.Session 对象"""
    session = requests.Session()
    yield session  # 返回 Session 供测试用例使用
    session.close()  # 测试结束后关闭 Session

# —————— session共享 ctx ——————
@pytest.fixture(scope="session")
def shared_ctx():
    # session 级别创建一次，整个测试会话内保持同一个 dict
    return {}

# —————— 每个 module 运行前后重置 ctx ——————
@pytest.fixture(scope="module", autouse=True)
def reset_ctx_per_module(shared_ctx):
    # 在本 module 的第一个测试用例运行前，清空 shared_ctx
    shared_ctx.clear()
    yield
