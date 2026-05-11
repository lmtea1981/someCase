"""
===================================
@Author: Djl
@Date: 2026/5/7 15:07
@Description: 
===================================
"""
# -*- coding: utf-8 -*-
import json
import re
import requests
from config.llm_config import LLM_MODE, OLLAMA_CONFIG, ONLINE_LLM_CONFIG, LLM_PROMPT

class LLMAnalyzer:
    def analyze(self, history):
        data = json.dumps(history, ensure_ascii=False)
        prompt = LLM_PROMPT + "\n压测数据：" + data

        print(f"提示词：{prompt}")

        # if LLM_MODE == "local":
        #     return self._ollama(prompt)
        # else:
        #     return self._online(prompt)

    def _ollama(self, prompt):
        try:
            resp = requests.post(
                f"{OLLAMA_CONFIG['host']}/api/generate",
                json={"model": OLLAMA_CONFIG["model"], "prompt": prompt, "stream": False},
                timeout=120
            )
            txt = resp.json()["response"]
            match = re.search(r"\{.*\}", txt, re.DOTALL)
            return json.loads(match.group(0)) if match else self._default()
        except:
            return self._default()

    def _online(self, prompt):
        try:
            headers = {"Authorization": f"Bearer {ONLINE_LLM_CONFIG['api_key']}"}
            data = {"model": ONLINE_LLM_CONFIG["model"], "messages": [{"role": "user", "content": prompt}]}
            resp = requests.post(ONLINE_LLM_CONFIG["base_url"] + "/chat/completions", headers=headers, json=data)
            txt = resp.json()["choices"][0]["message"]["content"]
            match = re.search(r"\{.*\}", txt, re.DOTALL)
            return json.loads(match.group(0)) if match else self._default()
        except:
            return self._default()

    def _default(self):
        return {
            "is_abnormal": False,
            "re_test": False,
            "recommend_concurrency": 50,
            "reason": "LLM解析完成，使用拐点前最优并发"
        }
