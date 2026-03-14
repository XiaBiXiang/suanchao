"""
LLM 服务模块
使用 LangChain 集成大语言模型
"""

import asyncio
import hashlib
import json
import re
from typing import Any, AsyncGenerator, Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings


# 系统提示词模板
SYSTEM_PROMPT = """你是一个严谨的算法导师。请根据用户的【题目描述】和【当前代码】，解答用户的疑问。

规则：
1. 绝对不要直接给出完整正确的代码
2. 而是指出当前的逻辑漏洞或语法错误
3. 给出引导性的提示，帮助用户自己思考出答案
4. 如果用户代码没有明显错误，可以给出优化建议
5. 保持友好、耐心的态度
6. 如果用户遇到困难，可以给出适当的代码片段作为参考，但不能是完整答案

回答格式要求：
- 使用清晰的结构
- 适当使用代码块展示错误位置
- 在关键地方给出提示，而不是直接告诉答案"""

PROBLEM_GENERATOR_PROMPT = """你是一个专业算法出题器。请根据要求生成一道可编程求解的算法题。

要求：
1. 输出必须是严格 JSON，不要输出额外说明文字。
2. 题目应包含清晰输入/输出定义和示例。
3. 题目难度需匹配 level(1-10) 和 mode。
4. test_cases 至少 3 个，至少 1 个隐藏用例(is_hidden=true)。
5. test_cases 的 input_data/expected_output 必须是纯文本，便于判题系统使用。
6. difficulty_label 仅允许 Easy/Medium/Hard。
7. time_limit 范围 500-5000，memory_limit 范围 64-512。
8. title 和 description_markdown 必须使用中文书写，不能使用英文题干或英文标题。
9. 避免总是产出“数组两数之和”这类过度常见模板，题型应尽量多样化。
10. 如果给了“需避开的历史题目”，新题的题意、输入输出和核心目标必须明显不同。

JSON 结构：
{
  "title": "题目标题",
  "description_markdown": "Markdown 题目描述",
  "difficulty_label": "Easy|Medium|Hard",
  "time_limit": 1000,
  "memory_limit": 128,
  "test_cases": [
    {"input_data": "...", "expected_output": "...", "is_hidden": false}
  ]
}"""


class LLMService:
    """
    LLM 服务类

    提供流式输出的 AI 对话能力
    """

    def __init__(self):
        """
        初始化 LLM
        """
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.7,
            streaming=True,
            max_tokens=2000,
            timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
            max_retries=1,
        )

        # 检查配置是否有效
        if settings.OPENAI_API_KEY == "sk-deepseek-your-api-key-here":
            print("警告: 请在 .env 文件或 config.py 中配置 DeepSeek API Key")

    async def chat_stream(
        self,
        problem_description: str,
        current_code: str,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        流式对话

        Args:
            problem_description: 题目描述
            current_code: 用户当前代码
            user_message: 用户消息

        Yields:
            str: 流式输出的文本片段
        """
        # 构建完整的上下文
        full_context = f"""【题目描述】
{problem_description}

【当前代码】
```{"python" if "python" in current_code.lower() else ""}
{current_code}
```

【用户问题】
{user_message}

请根据以上信息，帮助用户解决问题。"""

        # 创建消息列表
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=full_context),
        ]

        # 异步流式生成
        try:
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            yield f"error: {str(e)}"

    def _fallback_template_pool(self, difficulty: str) -> list[Dict[str, Any]]:
        easy_pool = [
            {
                "title": "基础训练：数组极差",
                "description_markdown": (
                    "给定一个长度为 `n` 的整数数组，输出数组中的最大值与最小值之差。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入整数 `n`\n"
                    "- 第二行输入 `n` 个整数\n\n"
                    "### 输出格式\n"
                    "- 输出一个整数，表示 `max(nums) - min(nums)`"
                ),
                "time_limit": 1000,
                "memory_limit": 128,
                "test_cases": [
                    {"input_data": "5\n1 9 3 7 5", "expected_output": "8", "is_hidden": False},
                    {"input_data": "4\n10 10 10 10", "expected_output": "0", "is_hidden": False},
                    {
                        "input_data": "6\n-3 -8 4 1 0 -2",
                        "expected_output": "12",
                        "is_hidden": True,
                    },
                ],
            },
            {
                "title": "基础训练：相邻增长计数",
                "description_markdown": (
                    "给定一个长度为 `n` 的整数序列，统计有多少个位置 `i(2<=i<=n)` 满足 "
                    "`a[i] > a[i-1]`。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入整数 `n`\n"
                    "- 第二行输入 `n` 个整数\n\n"
                    "### 输出格式\n"
                    "- 输出满足条件的位置数量"
                ),
                "time_limit": 1000,
                "memory_limit": 128,
                "test_cases": [
                    {"input_data": "5\n1 2 2 4 5", "expected_output": "3", "is_hidden": False},
                    {"input_data": "4\n9 7 5 3", "expected_output": "0", "is_hidden": False},
                    {
                        "input_data": "7\n1 3 2 4 4 8 6",
                        "expected_output": "3",
                        "is_hidden": True,
                    },
                ],
            },
            {
                "title": "基础训练：最长连续相同字符",
                "description_markdown": (
                    "给定一个仅包含小写字母的字符串 `s`，求其中最长连续相同字符段的长度。\n\n"
                    "### 输入格式\n"
                    "- 输入一行字符串 `s`\n\n"
                    "### 输出格式\n"
                    "- 输出一个整数，表示最长连续相同字符段长度"
                ),
                "time_limit": 1000,
                "memory_limit": 128,
                "test_cases": [
                    {"input_data": "aaabbccccd", "expected_output": "4", "is_hidden": False},
                    {"input_data": "abcdef", "expected_output": "1", "is_hidden": False},
                    {"input_data": "aabbaaaacc", "expected_output": "4", "is_hidden": True},
                ],
            },
        ]

        medium_pool = [
            {
                "title": "进阶训练：最长无重复子串",
                "description_markdown": (
                    "给定字符串 `s`，请返回不含重复字符的最长子串长度。\n\n"
                    "### 输入格式\n"
                    "- 输入一行字符串 `s`\n\n"
                    "### 输出格式\n"
                    "- 输出一个整数表示答案"
                ),
                "time_limit": 1500,
                "memory_limit": 192,
                "test_cases": [
                    {"input_data": "abcabcbb", "expected_output": "3", "is_hidden": False},
                    {"input_data": "bbbbb", "expected_output": "1", "is_hidden": False},
                    {"input_data": "pwwkew", "expected_output": "3", "is_hidden": True},
                ],
            },
            {
                "title": "进阶训练：和为 K 的子数组个数",
                "description_markdown": (
                    "给定整数数组 `nums` 和整数 `k`，求连续子数组和恰好等于 `k` 的个数。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入 `n k`\n"
                    "- 第二行输入 `n` 个整数\n\n"
                    "### 输出格式\n"
                    "- 输出一个整数表示满足条件的子数组数量"
                ),
                "time_limit": 1800,
                "memory_limit": 192,
                "test_cases": [
                    {"input_data": "3 2\n1 1 1", "expected_output": "2", "is_hidden": False},
                    {"input_data": "5 3\n1 2 1 2 1", "expected_output": "4", "is_hidden": False},
                    {
                        "input_data": "6 0\n1 -1 0 2 -2 0",
                        "expected_output": "10",
                        "is_hidden": True,
                    },
                ],
            },
            {
                "title": "进阶训练：区间合并",
                "description_markdown": (
                    "给定 `m` 个闭区间 `[l, r]`，请将有重叠的区间合并，按左端点升序输出。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入整数 `m`\n"
                    "- 接下来 `m` 行，每行输入两个整数 `l r`\n\n"
                    "### 输出格式\n"
                    "- 每行输出一个合并后的区间 `l r`"
                ),
                "time_limit": 1800,
                "memory_limit": 192,
                "test_cases": [
                    {
                        "input_data": "4\n1 3\n2 6\n8 10\n15 18",
                        "expected_output": "1 6\n8 10\n15 18",
                        "is_hidden": False,
                    },
                    {
                        "input_data": "3\n1 4\n4 5\n6 7",
                        "expected_output": "1 5\n6 7",
                        "is_hidden": False,
                    },
                    {
                        "input_data": "5\n1 2\n3 4\n2 3\n10 12\n11 13",
                        "expected_output": "1 4\n10 13",
                        "is_hidden": True,
                    },
                ],
            },
        ]

        hard_pool = [
            {
                "title": "高阶训练：滑动窗口最大值",
                "description_markdown": (
                    "给定长度为 `n` 的数组和窗口大小 `k`，输出每个窗口内的最大值。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入 `n k`\n"
                    "- 第二行输入 `n` 个整数\n\n"
                    "### 输出格式\n"
                    "- 输出 `n-k+1` 个整数（空格分隔）"
                ),
                "time_limit": 2500,
                "memory_limit": 256,
                "test_cases": [
                    {
                        "input_data": "8 3\n1 3 -1 -3 5 3 6 7",
                        "expected_output": "3 3 5 5 6 7",
                        "is_hidden": False,
                    },
                    {
                        "input_data": "5 2\n9 7 5 3 1",
                        "expected_output": "9 7 5 3",
                        "is_hidden": False,
                    },
                    {
                        "input_data": "6 4\n4 2 12 3 8 7",
                        "expected_output": "12 12 12",
                        "is_hidden": True,
                    },
                ],
            },
            {
                "title": "高阶训练：接雨水总量",
                "description_markdown": (
                    "给定表示柱子高度的数组，计算下雨后可以接到的雨水总量。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入整数 `n`\n"
                    "- 第二行输入 `n` 个非负整数\n\n"
                    "### 输出格式\n"
                    "- 输出一个整数，表示可接雨水总量"
                ),
                "time_limit": 2500,
                "memory_limit": 256,
                "test_cases": [
                    {
                        "input_data": "12\n0 1 0 2 1 0 1 3 2 1 2 1",
                        "expected_output": "6",
                        "is_hidden": False,
                    },
                    {"input_data": "6\n4 2 0 3 2 5", "expected_output": "9", "is_hidden": False},
                    {"input_data": "5\n5 4 3 2 1", "expected_output": "0", "is_hidden": True},
                ],
            },
            {
                "title": "高阶训练：最小覆盖子串",
                "description_markdown": (
                    "给定字符串 `s` 和 `t`，请在 `s` 中找出包含 `t` 全部字符的最短子串。\n\n"
                    "### 输入格式\n"
                    "- 第一行输入字符串 `s`\n"
                    "- 第二行输入字符串 `t`\n\n"
                    "### 输出格式\n"
                    "- 输出最短覆盖子串；若不存在则输出空串"
                ),
                "time_limit": 2800,
                "memory_limit": 256,
                "test_cases": [
                    {"input_data": "ADOBECODEBANC\nABC", "expected_output": "BANC", "is_hidden": False},
                    {"input_data": "aa\naa", "expected_output": "aa", "is_hidden": False},
                    {"input_data": "abcdebdde\nbde", "expected_output": "bcde", "is_hidden": True},
                ],
            },
        ]

        if difficulty == "Easy":
            return easy_pool
        if difficulty == "Medium":
            return medium_pool
        return hard_pool

    def _fallback_problem(
        self,
        level: int,
        mode: str = "",
        user_context: str = "",
        avoid_context: str = "",
        attempt: int = 1,
    ) -> Dict[str, Any]:
        difficulty = self._level_to_difficulty(level)
        pool = self._fallback_template_pool(difficulty)
        base_seed_payload = f"{level}|{mode}|{user_context}|{avoid_context}"
        base_seed_hash = hashlib.sha256(base_seed_payload.encode("utf-8")).hexdigest()
        start_idx = int(base_seed_hash[:8], 16) % max(1, len(pool))
        idx = (start_idx + max(0, attempt - 1)) % max(1, len(pool))
        template = pool[idx]

        return {
            "title": template["title"],
            "description_markdown": template["description_markdown"],
            "difficulty_label": difficulty,
            "time_limit": int(template["time_limit"]),
            "memory_limit": int(template["memory_limit"]),
            "test_cases": [dict(case) for case in template["test_cases"]],
            "generation_source": "fallback",
            "generation_note": f"AI 服务暂不可用，已使用本地备用题目模板（{difficulty}#{idx + 1}）。",
        }

    def _level_to_difficulty(self, level: int) -> str:
        if level <= 3:
            return "Easy"
        if level <= 7:
            return "Medium"
        return "Hard"

    def _contains_chinese(self, text: str) -> bool:
        return bool(re.search(r"[\u4e00-\u9fff]", text or ""))

    def _extract_json_object(self, raw_text: str) -> Dict[str, Any]:
        text = raw_text.strip()
        fenced = re.search(r"```json\s*(\{[\s\S]*\})\s*```", text)
        if fenced:
            text = fenced.group(1)
        else:
            first = text.find("{")
            last = text.rfind("}")
            if first != -1 and last != -1 and last > first:
                text = text[first : last + 1]
        return json.loads(text)

    def _normalize_problem(
        self,
        payload: Dict[str, Any],
        level: int,
        mode: str = "",
        user_context: str = "",
        avoid_context: str = "",
        attempt: int = 1,
    ) -> Dict[str, Any]:
        fallback = self._fallback_problem(
            level=level,
            mode=mode,
            user_context=user_context,
            avoid_context=avoid_context,
            attempt=attempt,
        )
        title = str(payload.get("title") or "").strip() or fallback["title"]
        description = str(payload.get("description_markdown") or "").strip() or fallback[
            "description_markdown"
        ]

        # 面向中文用户：标题和题干必须含中文，不满足则回退到中文模板
        if not self._contains_chinese(title):
            title = fallback["title"]
        if not self._contains_chinese(description):
            description = fallback["description_markdown"]

        difficulty = str(payload.get("difficulty_label") or "").strip()
        if difficulty not in {"Easy", "Medium", "Hard"}:
            difficulty = self._level_to_difficulty(level)

        try:
            time_limit = int(payload.get("time_limit", 1000))
        except Exception:
            time_limit = 1000
        time_limit = max(500, min(5000, time_limit))

        try:
            memory_limit = int(payload.get("memory_limit", 128))
        except Exception:
            memory_limit = 128
        memory_limit = max(64, min(512, memory_limit))

        test_cases_raw = payload.get("test_cases", [])
        normalized_cases = []
        if isinstance(test_cases_raw, list):
            for case in test_cases_raw:
                if not isinstance(case, dict):
                    continue
                input_data = str(case.get("input_data", "")).strip()
                expected_output = str(case.get("expected_output", "")).strip()
                if not input_data or not expected_output:
                    continue
                normalized_cases.append(
                    {
                        "input_data": input_data,
                        "expected_output": expected_output,
                        "is_hidden": bool(case.get("is_hidden", False)),
                    }
                )

        if len(normalized_cases) < 3:
            normalized_cases = fallback["test_cases"]

        # 至少保留一个隐藏用例
        if not any(case["is_hidden"] for case in normalized_cases):
            normalized_cases[-1]["is_hidden"] = True

        return {
            "title": title,
            "description_markdown": description,
            "difficulty_label": difficulty,
            "time_limit": time_limit,
            "memory_limit": memory_limit,
            "test_cases": normalized_cases,
        }

    async def generate_problem(
        self,
        level: int,
        mode: str,
        user_context: str = "",
        avoid_context: str = "",
        attempt: int = 1,
    ) -> Dict[str, Any]:
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.9,
            streaming=False,
            max_tokens=2600,
            timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
            max_retries=1,
        )

        avoid_context_text = (avoid_context or "").strip()
        avoid_block = ""
        if avoid_context_text:
            # 控制长度，避免 prompt 过大
            avoid_block = (
                "需避开以下已存在或已拒绝题目（新题题意、输入输出与核心目标必须明显不同）：\n"
                f"{avoid_context_text[:2400]}\n"
            )

        prompt = (
            f"mode={mode}\n"
            f"level={level}\n"
            f"attempt={attempt}\n"
            f"user_context={user_context or '无'}\n"
            f"{avoid_block}"
            "请生成一题适合该水平的算法题。"
        )

        try:
            response = await asyncio.wait_for(
                llm.ainvoke(
                    [
                        SystemMessage(content=PROBLEM_GENERATOR_PROMPT),
                        HumanMessage(content=prompt),
                    ]
                ),
                timeout=settings.AI_GENERATE_TIMEOUT_SECONDS,
            )
            content = response.content if hasattr(response, "content") else str(response)
            parsed = self._extract_json_object(str(content))
            normalized = self._normalize_problem(
                payload=parsed,
                level=level,
                mode=mode,
                user_context=user_context,
                avoid_context=avoid_context,
                attempt=attempt,
            )
            normalized["generation_source"] = "llm"
            normalized["generation_note"] = ""
            return normalized
        except asyncio.TimeoutError:
            print("AI 出题超时，已回退到本地题目模板")
            return self._fallback_problem(
                level=level,
                mode=mode,
                user_context=user_context,
                avoid_context=avoid_context,
                attempt=attempt,
            )
        except Exception as e:
            print(f"AI 出题失败，已回退到本地题目模板: {e}")
            return self._fallback_problem(
                level=level,
                mode=mode,
                user_context=user_context,
                avoid_context=avoid_context,
                attempt=attempt,
            )


# 创建全局 LLM 服务实例
llm_service = LLMService()


async def get_llm_response(
    problem_description: str,
    current_code: str,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """
    便捷函数：获取 LLM 流式响应

    Args:
        problem_description: 题目描述
        current_code: 用户当前代码
        user_message: 用户消息

    Yields:
        str: 流式输出的文本片段
    """
    async for chunk in llm_service.chat_stream(
        problem_description=problem_description,
        current_code=current_code,
        user_message=user_message,
    ):
        yield chunk


async def generate_ai_problem(
    level: int,
    mode: str,
    user_context: str = "",
    avoid_context: str = "",
    attempt: int = 1,
) -> Dict[str, Any]:
    """
    便捷函数：生成 AI 题目
    """
    return await llm_service.generate_problem(
        level=level,
        mode=mode,
        user_context=user_context,
        avoid_context=avoid_context,
        attempt=attempt,
    )
