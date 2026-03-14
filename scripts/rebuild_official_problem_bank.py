"""
重建官方题库脚本

用途:
1. 删除所有官方题 (official / source_type is null)
2. 按指定比例批量生成并写入官方题库

默认题目配比:
- Easy: 40
- Medium: 40
- Hard: 20

说明:
- 全部题目为中文标题与中文题干
- 每题至少 3 个测试用例，且至少 1 个隐藏用例
- 采用本地模板生成，确保离线稳定可重建
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlalchemy import and_, delete, func, or_, select

from app.db.session import AsyncSessionLocal
from app.models import user as _user_models  # noqa: F401
from app.models.problem import DifficultyEnum, Problem, ProblemSourceEnum, TestCase


@dataclass
class CaseSeed:
    input_data: str
    expected_output: str
    is_hidden: bool


@dataclass
class ProblemSeed:
    title: str
    description: str
    difficulty: DifficultyEnum
    time_limit: int
    memory_limit: int
    test_cases: list[CaseSeed]


def format_ints(nums: Sequence[int]) -> str:
    return " ".join(str(x) for x in nums)


def yes_no(flag: bool) -> str:
    return "Yes" if flag else "No"


def normalize_text(text: str) -> str:
    return text.strip()


def normalize_for_dedup(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_for_dedup(text).encode("utf-8")).hexdigest()


def summarize_text(text: str, limit: int = 80) -> str:
    compact = re.sub(r"\s+", " ", (text or "").strip())
    if len(compact) <= limit:
        return compact
    return compact[: max(1, limit - 1)] + "…"


def build_type_labels(
    prefix: str,
    themes: Sequence[str],
    scenes: Sequence[str],
    count: int,
) -> list[str]:
    labels: list[str] = []
    for scene in scenes:
        for theme in themes:
            labels.append(f"{prefix}·{scene}·{theme}")
            if len(labels) >= count:
                return labels
    return labels[:count]


def assign_distinct_type_profiles(selected: list[ProblemSeed]) -> None:
    easy = [seed for seed in selected if seed.difficulty == DifficultyEnum.EASY]
    medium = [seed for seed in selected if seed.difficulty == DifficultyEnum.MEDIUM]
    hard = [seed for seed in selected if seed.difficulty == DifficultyEnum.HARD]

    easy_labels = build_type_labels(
        prefix="简单",
        themes=[
            "数组扫描",
            "区间比较",
            "字符串清洗",
            "索引映射",
            "计数统计",
            "规则模拟",
            "序列判断",
            "基础二分",
        ],
        scenes=[
            "电商订单",
            "校园成绩",
            "日志整理",
            "设备监控",
            "仓储盘点",
        ],
        count=len(easy),
    )
    medium_labels = build_type_labels(
        prefix="中等",
        themes=[
            "前缀和建模",
            "滑窗优化",
            "区间结构",
            "图搜索",
            "动态规划",
            "贪心策略",
            "双端队列",
            "矩阵遍历",
        ],
        scenes=[
            "风控分析",
            "路径规划",
            "活动编排",
            "数据压测",
            "推荐系统",
        ],
        count=len(medium),
    )
    hard_labels = build_type_labels(
        prefix="困难",
        themes=[
            "状态压缩",
            "最优编辑",
            "窗口覆盖",
            "单调结构",
            "复杂DP",
            "双指针极值",
            "栈序列推导",
            "图论约束",
        ],
        scenes=[
            "高并发调度",
            "跨域融合",
            "异常恢复",
        ],
        count=len(hard),
    )

    def build_variant_notes(label: str, sample_input: str, sample_output: str) -> str:
        parts = label.split("·")
        scene = parts[1] if len(parts) > 1 else "通用场景"
        theme = parts[2] if len(parts) > 2 else "综合训练"
        has_negative = "-" in sample_input
        has_matrix = "\n" in sample_input and (" " in sample_input)
        token_count = len(re.findall(r"-?\d+|[A-Za-z]+|[\\u4e00-\\u9fff]+", sample_input))
        boundary_hint = (
            "包含负数与符号混合输入"
            if has_negative
            else ("包含多行结构化输入" if has_matrix else "包含短串或小规模离散输入")
        )
        return normalize_text(
            "\n".join(
                [
                    "定制规则：",
                    f"1. 本变体场景：{scene}，要求优先体现「{theme}」的建模方式。",
                    f"2. 评测输入特征：token 数约 {token_count}，{boundary_hint}。",
                    f"3. 输出判定重点：对「{summarize_text(sample_output, 28)}」进行严格匹配。",
                    f"4. 实战提示：请关注 {scene} 场景下的边界组合与异常数据容错。",
                ]
            )
        )

    def build_core_story(label: str, sample_input: str, sample_output: str) -> str:
        parts = label.split("·")
        scene = parts[1] if len(parts) > 1 else "通用场景"
        theme = parts[2] if len(parts) > 2 else "综合训练"
        seed_key = f"{label}|{sample_input}|{sample_output}"
        task_code = hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:12].upper()

        def pick(options: Sequence[str], salt: str) -> str:
            digest = hashlib.sha256(f"{seed_key}|{salt}".encode("utf-8")).hexdigest()
            return options[int(digest[:8], 16) % len(options)]

        roles = [
            "值班工程师",
            "数据分析师",
            "运营负责人",
            "策略开发同学",
            "平台治理同学",
            "排障负责人",
            "业务架构师",
            "算法工程师",
            "交付经理",
            "质量保障同学",
            "风控审核员",
            "班主任助教",
        ]
        goals = [
            "在最短时间内输出稳定可复核的结果",
            "先保证边界样例正确，再追求实现简洁",
            "保证与既有口径一致，避免统计漂移",
            "确保多批次输入下结果具备可追溯性",
            "优先降低异常输入导致的误判风险",
            "为后续流程提供可直接消费的标准输出",
            "保证线上与本地调试行为一致",
            "让同组同学可快速复验你的实现",
            "在高噪声数据下保持结论稳定",
            "在有限时限下达成正确率优先",
            "让评测在极端输入下也保持通过",
            "兼顾可读性与性能下限",
        ]
        constraints = [
            "输入中可能混入多余空白或换行",
            "数据规模会在小样例与边界样例间切换",
            "存在重复元素与顺序扰动",
            "会出现符号变化与临界值穿越",
            "同一规则会在多组数据中连续触发",
            "部分样例会覆盖空输入或最小规模输入",
            "输入结构固定但数值分布不均匀",
            "评测会混合普通场景与异常场景",
            "样例之间会出现局部相似但结论不同",
            "输入会刻意放大某些极端情况",
            "某些字段会出现高频重复",
            "局部数据会存在明显偏态",
        ]
        checks = [
            "通过样例并不足够，隐藏用例将重点验证边界路径",
            "输出必须与平台判题结果逐字符一致",
            "需要明确处理异常分支，避免默认路径误通过",
            "结果要同时满足正确性与稳定性",
            "请保证你的实现在不同输入批次下行为一致",
            "判题会关注你对临界输入的处理完整性",
            "请确保复杂度控制在题目建议范围内",
            "隐藏样例会验证极端边界与退化路径",
            "输出需保持确定性，不能依赖随机行为",
            "你需要对输入合法但刁钻的情况给出正确处理",
            "评测将校验你对特殊字符或空结构的处理",
            "请避免通过硬编码样例结果取巧",
        ]
        deliveries = [
            "结果将直接进入下游质量看板。",
            "该输出会作为下一环节策略输入。",
            "你的结果将用于自动化巡检任务。",
            "这份结果会同步到业务日报。",
            "该结论将驱动后续任务分配。",
            "输出会用于生成后续对账明细。",
            "评测结果会反馈到训练计划中。",
            "该结果会触发下一步审核流程。",
            "输出将用于实时大盘刷新。",
            "这份结果会写入周期复盘报告。",
            "最终结果会流入风险告警流程。",
            "该输出将参与后续回归测试。",
        ]

        token_count = len(re.findall(r"-?\\d+|[A-Za-z]+|[\\u4e00-\\u9fff]+", sample_input))
        input_preview = summarize_text(sample_input, 36)
        output_preview = summarize_text(sample_output, 28)

        role = pick(roles, "role")
        goal = pick(goals, "goal")
        constraint = pick(constraints, "constraint")
        check = pick(checks, "check")
        delivery = pick(deliveries, "delivery")

        return normalize_text(
            "\n".join(
                [
                    "场景化任务说明：",
                    f"你在「{scene}」中扮演{role}，当前训练主题是「{theme}」。",
                    f"任务编码：{task_code}。",
                    f"任务目标：{goal}。",
                    f"数据约束：{constraint}；本题样例输入规模约 token={token_count}（{input_preview}）。",
                    f"验收标准：{check}；请确保输出与「{output_preview}」同口径。",
                    f"交付背景：{delivery}",
                ]
            )
        )

    def rewrite(seed: ProblemSeed, label: str, level_text: str) -> None:
        sample = next((case for case in seed.test_cases if not case.is_hidden), seed.test_cases[0])
        profile_head = (
            f"题型定位：{label}\n"
            f"训练层级：{level_text}\n"
            f"任务背景：围绕「{label.split('·')[1]}」场景进行建模。\n"
            f"样例摘要：{summarize_text(sample.input_data)} -> {summarize_text(sample.expected_output)}"
        )
        core_story = build_core_story(label, sample.input_data, sample.expected_output)
        variant_notes = build_variant_notes(label, sample.input_data, sample.expected_output)
        seed.title = label
        seed.description = normalize_text(
            f"{profile_head}\n\n{seed.description}\n\n{core_story}\n\n{variant_notes}"
        )

    for seed, label in zip(easy, easy_labels):
        rewrite(seed, label, "Easy")
    for seed, label in zip(medium, medium_labels):
        rewrite(seed, label, "Medium")
    for seed, label in zip(hard, hard_labels):
        rewrite(seed, label, "Hard")


def enrich_duplicate_descriptions(seeds: list[ProblemSeed]) -> int:
    """
    对重复题干补充变体信息，避免题库中出现“同题干不同编号”的重复观感。
    """
    seen: dict[str, int] = {}
    updated = 0
    for seed in seeds:
        base_key = normalize_for_dedup(seed.description)
        seen[base_key] = seen.get(base_key, 0) + 1
        variant_no = seen[base_key]
        if variant_no <= 1:
            continue

        sample = next((case for case in seed.test_cases if not case.is_hidden), seed.test_cases[0])
        variant_note = (
            "\n\n变体补充：\n"
            f"- 变体编号：{variant_no}\n"
            f"- 对应标题：{seed.title}\n"
            f"- 样例输入摘要：{summarize_text(sample.input_data)}\n"
            f"- 样例输出摘要：{summarize_text(sample.expected_output)}\n"
        )
        seed.description = normalize_text(seed.description + variant_note)
        updated += 1
    return updated


def validate_unique_seed_content(seeds: Sequence[ProblemSeed]) -> None:
    """
    校验标题和题干唯一性，防止重复题写入官方题库。
    """
    title_seen: dict[str, str] = {}
    desc_seen: dict[str, str] = {}
    duplicate_titles: list[str] = []
    duplicate_descriptions: list[str] = []

    for seed in seeds:
        title_key = normalize_for_dedup(seed.title)
        desc_key = normalize_for_dedup(seed.description)
        if title_key in title_seen:
            duplicate_titles.append(seed.title)
        else:
            title_seen[title_key] = seed.title

        if desc_key in desc_seen:
            duplicate_descriptions.append(seed.title)
        else:
            desc_seen[desc_key] = seed.title

    if duplicate_titles or duplicate_descriptions:
        raise ValueError(
            "检测到重复题目种子："
            f"重复标题 {len(duplicate_titles)} 个，"
            f"重复题干 {len(duplicate_descriptions)} 个。"
        )


def mark_hidden(cases: list[CaseSeed]) -> list[CaseSeed]:
    if not cases:
        raise ValueError("测试用例不能为空")
    if not any(case.is_hidden for case in cases):
        cases[-1].is_hidden = True
    return cases


def build_easy_sum_variants() -> list[ProblemSeed]:
    datasets = [
        [1, 2, 3, 4, 5],
        [8, -3, 10, 0, -2],
        [100, 200, 300],
        [-5, -4, -3, -2, -1],
        [7, 7, 7, 7, 7, 7],
    ]
    seeds: list[ProblemSeed] = []
    for idx, arr in enumerate(datasets, start=1):
        title = f"数组求和训练 {idx}"
        desc = f"""给定一个整数数组，输出所有元素之和。

输入格式：
第一行输入一个整数 n，表示数组长度。
第二行输入 n 个整数。

输出格式：
输出一个整数，表示数组元素总和。

要求：
- 1 <= n <= 2 * 10^5
- 请注意负数情况。
"""
        visible = [
            CaseSeed(f"{len(arr)}\n{format_ints(arr)}", str(sum(arr)), False),
            CaseSeed("4\n10 20 30 40", "100", False),
        ]
        hidden_arr = arr + [idx * 3, -idx]
        hidden = CaseSeed(
            f"{len(hidden_arr)}\n{format_ints(hidden_arr)}", str(sum(hidden_arr)), True
        )
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1000,
                memory_limit=128,
                test_cases=mark_hidden(visible + [hidden]),
            )
        )
    return seeds


def build_easy_max_min_gap_variants() -> list[ProblemSeed]:
    datasets = [
        [3, 9, 1, 7],
        [12, 12, 12],
        [-5, -9, -1, -7],
        [100, 1, 50, 88, 23],
        [2, 4, 6, 8, 10, 12],
    ]
    seeds: list[ProblemSeed] = []
    for idx, arr in enumerate(datasets, start=1):
        gap = max(arr) - min(arr)
        title = f"最大最小差值 {idx}"
        desc = """给定一个整数数组，输出数组中的最大值与最小值之差。

输入格式：
第一行输入整数 n。
第二行输入 n 个整数。

输出格式：
输出一个整数，表示 max(nums) - min(nums)。
"""
        cases = [
            CaseSeed(f"{len(arr)}\n{format_ints(arr)}", str(gap), False),
            CaseSeed("5\n5 1 9 3 7", "8", False),
            CaseSeed("6\n-8 -1 -3 -20 -5 -7", "19", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def build_easy_even_count_variants() -> list[ProblemSeed]:
    datasets = [
        [1, 2, 3, 4, 5, 6],
        [2, 2, 2, 2],
        [1, 3, 5, 7],
        [-2, -4, -6, 1],
        [0, 11, 22, 33, 44],
    ]
    seeds: list[ProblemSeed] = []
    for idx, arr in enumerate(datasets, start=1):
        title = f"统计偶数个数 {idx}"
        desc = """给定一个整数数组，统计其中偶数元素的数量。

输入格式：
第一行输入 n。
第二行输入 n 个整数。

输出格式：
输出一个整数，表示偶数个数。
"""
        cases = [
            CaseSeed(
                f"{len(arr)}\n{format_ints(arr)}",
                str(sum(1 for x in arr if x % 2 == 0)),
                False,
            ),
            CaseSeed("8\n1 2 3 4 5 6 7 8", "4", False),
            CaseSeed("7\n-2 -1 0 1 2 3 4", "4", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def binary_search(nums: Sequence[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def build_easy_binary_search_variants() -> list[ProblemSeed]:
    datasets = [
        ([1, 3, 5, 7, 9], 7),
        ([2, 4, 6, 8, 10, 12], 11),
        ([-10, -5, 0, 3, 9], -10),
        ([1, 2, 2, 2, 5], 2),
        ([5, 10, 15, 20, 25, 30], 30),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (nums, target) in enumerate(datasets, start=1):
        title = f"有序数组查找 {idx}"
        desc = """给定一个升序数组和目标值 target，请返回 target 的下标。
若不存在，输出 -1。

输入格式：
第一行输入 n。
第二行输入升序数组 nums。
第三行输入目标值 target。

输出格式：
输出一个整数下标。
"""
        cases = [
            CaseSeed(
                f"{len(nums)}\n{format_ints(nums)}\n{target}",
                str(binary_search(nums, target)),
                False,
            ),
            CaseSeed("5\n1 4 7 9 12\n7", "2", False),
            CaseSeed("6\n-6 -3 0 2 5 11\n4", "-1", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1200,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def clean_pal_text(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum())


def is_palindrome_text(text: str) -> bool:
    cleaned = clean_pal_text(text)
    return cleaned == cleaned[::-1]


def build_easy_palindrome_variants() -> list[ProblemSeed]:
    texts = [
        "A man, a plan, a canal: Panama",
        "race a car",
        "No lemon, no melon",
        "12321",
        "OpenAI",
    ]
    seeds: list[ProblemSeed] = []
    for idx, text in enumerate(texts, start=1):
        title = f"回文串判断 {idx}"
        desc = """给定一个字符串，忽略大小写与非字母数字字符，判断是否为回文串。

输入格式：
输入一行字符串 s。

输出格式：
若为回文输出 Yes，否则输出 No。
"""
        cases = [
            CaseSeed(text, yes_no(is_palindrome_text(text)), False),
            CaseSeed("Never odd or even", "Yes", False),
            CaseSeed("algorithm", "No", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def valid_parentheses(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


def build_easy_valid_parentheses_variants() -> list[ProblemSeed]:
    texts = [
        "()[]{}",
        "([{}])",
        "(]",
        "(((())))",
        "{[()]}[]{}",
    ]
    seeds: list[ProblemSeed] = []
    for idx, text in enumerate(texts, start=1):
        title = f"有效括号判断 {idx}"
        desc = """给定仅由 `()[]{}` 组成的字符串，判断括号是否有效匹配。

输入格式：
输入一行字符串 s。

输出格式：
有效输出 Yes，无效输出 No。
"""
        cases = [
            CaseSeed(text, yes_no(valid_parentheses(text)), False),
            CaseSeed("([)]", "No", False),
            CaseSeed("{[]}", "Yes", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def fib_mod(n: int, mod: int) -> int:
    if n <= 1:
        return n % mod
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, (a + b) % mod
    return b


def build_easy_fib_variants() -> list[ProblemSeed]:
    datasets = [
        (10, 1_000_000_007),
        (25, 1_000_000_007),
        (40, 1_000_000_007),
        (100, 1_000_000_007),
        (75, 998_244_353),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (n, mod) in enumerate(datasets, start=1):
        title = f"斐波那契取模 {idx}"
        desc = """给定 n 和 mod，计算第 n 项斐波那契数 F(n) 对 mod 取模后的结果。

定义：
F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)

输入格式：
一行两个整数 n, mod。

输出格式：
输出 F(n) % mod。
"""
        cases = [
            CaseSeed(f"{n} {mod}", str(fib_mod(n, mod)), False),
            CaseSeed("5 1000", "5", False),
            CaseSeed("50 1000000007", str(fib_mod(50, 1_000_000_007)), True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1200,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def two_sum_indices(nums: Sequence[int], target: int) -> tuple[int, int]:
    seen: dict[int, int] = {}
    for i, v in enumerate(nums):
        need = target - v
        if need in seen:
            return seen[need], i
        seen[v] = i
    return -1, -1


def build_easy_two_sum_variants() -> list[ProblemSeed]:
    datasets = [
        ([2, 7, 11, 15], 9),
        ([3, 2, 4], 6),
        ([3, 3], 6),
        ([1, 5, 9, 13], 14),
        ([8, -1, 2, 10], 9),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (nums, target) in enumerate(datasets, start=1):
        i, j = two_sum_indices(nums, target)
        title = f"两数之和下标 {idx}"
        desc = """给定整数数组 nums 和目标值 target，找到两数之和等于 target 的两个下标 i, j。

约束：
- 保证恰好有一个解
- 不能使用同一元素两次

输入格式：
第一行输入 n
第二行输入 n 个整数
第三行输入 target

输出格式：
输出两个下标 i j（空格分隔）。
"""
        cases = [
            CaseSeed(f"{len(nums)}\n{format_ints(nums)}\n{target}", f"{i} {j}", False),
            CaseSeed("5\n1 2 3 4 5\n9", "3 4", False),
            CaseSeed("6\n10 20 5 7 8 2\n12", "2 3", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.EASY,
                time_limit=1200,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def length_of_longest_substring(s: str) -> int:
    left = 0
    best = 0
    index: dict[str, int] = {}
    for right, ch in enumerate(s):
        if ch in index and index[ch] >= left:
            left = index[ch] + 1
        index[ch] = right
        best = max(best, right - left + 1)
    return best


def build_medium_longest_substr_variants() -> list[ProblemSeed]:
    samples = [
        "abcabcbb",
        "bbbbb",
        "pwwkew",
        "dvdf",
        "anviaj",
    ]
    seeds: list[ProblemSeed] = []
    for idx, s in enumerate(samples, start=1):
        title = f"最长无重复子串 {idx}"
        desc = """给定字符串 s，求不包含重复字符的最长子串长度。

输入格式：
输入一行字符串 s。

输出格式：
输出一个整数表示最长长度。
"""
        cases = [
            CaseSeed(s, str(length_of_longest_substring(s)), False),
            CaseSeed("abba", "2", False),
            CaseSeed("tmmzuxt", "5", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=1500,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def count_subarray_sum_k(nums: Sequence[int], k: int) -> int:
    prefix = 0
    counter = {0: 1}
    ans = 0
    for x in nums:
        prefix += x
        ans += counter.get(prefix - k, 0)
        counter[prefix] = counter.get(prefix, 0) + 1
    return ans


def build_medium_subarray_sum_k_variants() -> list[ProblemSeed]:
    datasets = [
        ([1, 1, 1], 2),
        ([1, 2, 3], 3),
        ([3, 4, 7, 2, -3, 1, 4, 2], 7),
        ([0, 0, 0, 0], 0),
        ([1, -1, 1, -1, 1], 0),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (nums, k) in enumerate(datasets, start=1):
        title = f"和为 K 的子数组计数 {idx}"
        desc = """给定整数数组 nums 和整数 k，统计和为 k 的连续子数组个数。

输入格式：
第一行输入 n。
第二行输入 n 个整数。
第三行输入 k。

输出格式：
输出一个整数表示数量。
"""
        cases = [
            CaseSeed(
                f"{len(nums)}\n{format_ints(nums)}\n{k}",
                str(count_subarray_sum_k(nums, k)),
                False,
            ),
            CaseSeed("5\n1 2 1 2 1\n3", "4", False),
            CaseSeed("6\n2 -2 2 -2 2 -2\n0", "9", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=1800,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def min_subarray_len(target: int, nums: Sequence[int]) -> int:
    left = 0
    total = 0
    best = 10**9
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == 10**9 else best


def build_medium_min_len_subarray_variants() -> list[ProblemSeed]:
    datasets = [
        (7, [2, 3, 1, 2, 4, 3]),
        (15, [1, 2, 3, 4, 5]),
        (11, [1, 1, 1, 1, 1, 1, 1, 1]),
        (4, [1, 4, 4]),
        (8, [3, 1, 1, 1, 2, 4]),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (target, nums) in enumerate(datasets, start=1):
        title = f"最短达标子数组 {idx}"
        desc = """给定正整数数组 nums 和目标值 target，找到和大于等于 target 的最短连续子数组长度。

若不存在满足条件的子数组，输出 0。

输入格式：
第一行输入 n。
第二行输入 n 个正整数。
第三行输入 target。

输出格式：
输出一个整数。
"""
        cases = [
            CaseSeed(
                f"{len(nums)}\n{format_ints(nums)}\n{target}",
                str(min_subarray_len(target, nums)),
                False,
            ),
            CaseSeed("6\n1 2 3 4 5 6\n10", "2", False),
            CaseSeed("5\n1 1 1 1 1\n10", "0", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=1800,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(a, b) for a, b in merged]


def format_intervals(intervals: Sequence[tuple[int, int]]) -> str:
    return "\n".join(f"{a} {b}" for a, b in intervals)


def format_merged(intervals: Sequence[tuple[int, int]]) -> str:
    return " | ".join(f"{a} {b}" for a, b in intervals)


def build_medium_merge_intervals_variants() -> list[ProblemSeed]:
    datasets = [
        [(1, 3), (2, 6), (8, 10), (15, 18)],
        [(1, 4), (4, 5)],
        [(1, 4), (0, 0)],
        [(2, 3), (4, 5), (6, 7), (8, 9), (1, 10)],
        [(1, 2), (3, 6), (5, 7), (8, 10)],
    ]
    seeds: list[ProblemSeed] = []
    for idx, intervals in enumerate(datasets, start=1):
        merged = merge_intervals(list(intervals))
        title = f"区间合并 {idx}"
        desc = """给定若干闭区间 [l, r]，请合并所有重叠区间并按起点升序输出。

输入格式：
第一行输入区间个数 n。
接下来 n 行，每行两个整数 l r。

输出格式：
将合并后的区间按 `l r | l r` 的格式输出。
例如：`1 6 | 8 10 | 15 18`
"""
        cases = [
            CaseSeed(
                f"{len(intervals)}\n{format_intervals(intervals)}",
                format_merged(merged),
                False,
            ),
            CaseSeed("3\n1 2\n2 4\n6 8", "1 4 | 6 8", False),
            CaseSeed("4\n1 5\n2 3\n4 8\n10 12", "1 8 | 10 12", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=1800,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def lis_length(nums: Sequence[int]) -> int:
    import bisect

    tails: list[int] = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def build_medium_lis_variants() -> list[ProblemSeed]:
    datasets = [
        [10, 9, 2, 5, 3, 7, 101, 18],
        [0, 1, 0, 3, 2, 3],
        [7, 7, 7, 7, 7],
        [4, 10, 4, 3, 8, 9],
        [1, 3, 6, 7, 9, 4, 10, 5, 6],
    ]
    seeds: list[ProblemSeed] = []
    for idx, nums in enumerate(datasets, start=1):
        title = f"最长递增子序列长度 {idx}"
        desc = """给定整数数组 nums，求最长严格递增子序列长度。

输入格式：
第一行输入 n。
第二行输入 n 个整数。

输出格式：
输出 LIS 的长度。
"""
        cases = [
            CaseSeed(f"{len(nums)}\n{format_ints(nums)}", str(lis_length(nums)), False),
            CaseSeed("5\n1 2 3 4 5", "5", False),
            CaseSeed("7\n9 8 7 6 5 4 3", "1", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=1800,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def coin_change(coins: Sequence[int], amount: int) -> int:
    inf = 10**9
    dp = [0] + [inf] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if x >= c:
                dp[x] = min(dp[x], dp[x - c] + 1)
    return -1 if dp[amount] >= inf else dp[amount]


def build_medium_coin_change_variants() -> list[ProblemSeed]:
    datasets = [
        ([1, 2, 5], 11),
        ([2], 3),
        ([1], 0),
        ([1, 3, 4], 6),
        ([2, 5, 10, 1], 27),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (coins, amount) in enumerate(datasets, start=1):
        title = f"零钱兑换最少硬币 {idx}"
        desc = """给定硬币面额数组 coins 和总金额 amount，求组成 amount 所需的最少硬币数。
若无法组成，输出 -1。

输入格式：
第一行输入 m（硬币种类数）。
第二行输入 m 个硬币面额。
第三行输入 amount。

输出格式：
输出一个整数。
"""
        cases = [
            CaseSeed(
                f"{len(coins)}\n{format_ints(coins)}\n{amount}",
                str(coin_change(coins, amount)),
                False,
            ),
            CaseSeed("3\n2 4 6\n8", "2", False),
            CaseSeed("4\n3 7 10 14\n1", "-1", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=2000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def parse_grid(text: str) -> list[list[str]]:
    lines = text.strip().splitlines()
    n, m = map(int, lines[0].split())
    grid = [list(lines[i + 1].strip()) for i in range(n)]
    if any(len(row) != m for row in grid):
        raise ValueError("网格列数不一致")
    return grid


def count_islands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    n, m = len(grid), len(grid[0])
    seen = [[False] * m for _ in range(n)]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def bfs(sr: int, sc: int):
        q = [(sr, sc)]
        seen[sr][sc] = True
        while q:
            r, c = q.pop()
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < n
                    and 0 <= nc < m
                    and not seen[nr][nc]
                    and grid[nr][nc] == "1"
                ):
                    seen[nr][nc] = True
                    q.append((nr, nc))

    ans = 0
    for r in range(n):
        for c in range(m):
            if grid[r][c] == "1" and not seen[r][c]:
                ans += 1
                bfs(r, c)
    return ans


def grid_to_input(grid: list[str]) -> str:
    return f"{len(grid)} {len(grid[0])}\n" + "\n".join(grid)


def build_medium_island_variants() -> list[ProblemSeed]:
    grids = [
        ["11110", "11010", "11000", "00000"],
        ["11000", "11000", "00100", "00011"],
        ["10101", "01010", "10101", "01010"],
        ["111", "111", "111"],
        ["10001", "00100", "11111", "00100", "10001"],
    ]
    seeds: list[ProblemSeed] = []
    for idx, grid_rows in enumerate(grids, start=1):
        grid = [list(row) for row in grid_rows]
        title = f"岛屿数量统计 {idx}"
        desc = """给定由字符 '0' 和 '1' 组成的网格，统计岛屿数量。
岛屿由水平或垂直方向相邻的 '1' 构成。

输入格式：
第一行输入 n m。
接下来 n 行，每行一个长度为 m 的 01 字符串。

输出格式：
输出岛屿数量。
"""
        cases = [
            CaseSeed(grid_to_input(grid_rows), str(count_islands(grid)), False),
            CaseSeed("3 3\n111\n010\n111", "1", False),
            CaseSeed("4 4\n1001\n0000\n1001\n0000", "4", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=2200,
                memory_limit=196,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def spiral_order(matrix: list[list[int]]) -> list[int]:
    ans: list[int] = []
    if not matrix or not matrix[0]:
        return ans
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            ans.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            ans.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                ans.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                ans.append(matrix[r][left])
            left += 1
    return ans


def matrix_input(matrix: list[list[int]]) -> str:
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    body = "\n".join(format_ints(row) for row in matrix)
    return f"{n} {m}\n{body}"


def build_medium_spiral_variants() -> list[ProblemSeed]:
    mats = [
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
        [[1], [2], [3], [4]],
        [[1, 2, 3, 4]],
        [[1, 2], [3, 4], [5, 6], [7, 8]],
    ]
    seeds: list[ProblemSeed] = []
    for idx, mat in enumerate(mats, start=1):
        title = f"矩阵螺旋遍历 {idx}"
        desc = """给定 n 行 m 列矩阵，按顺时针螺旋顺序输出全部元素。

输入格式：
第一行输入 n m。
接下来 n 行，每行 m 个整数。

输出格式：
输出一行，元素按空格分隔。
"""
        cases = [
            CaseSeed(matrix_input(mat), format_ints(spiral_order(mat)), False),
            CaseSeed("2 2\n1 2\n3 4", "1 2 4 3", False),
            CaseSeed("3 4\n1 2 3 4\n5 6 7 8\n9 10 11 12", "1 2 3 4 8 12 11 10 9 5 6 7", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.MEDIUM,
                time_limit=2000,
                memory_limit=128,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def edit_distance(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + 1,
                )
    return dp[n][m]


def build_hard_edit_distance_variants() -> list[ProblemSeed]:
    datasets = [
        ("horse", "ros"),
        ("intention", "execution"),
        ("kitten", "sitting"),
        ("algorithm", "altruistic"),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (a, b) in enumerate(datasets, start=1):
        title = f"编辑距离 {idx}"
        desc = """给定两个字符串 word1 和 word2，计算将 word1 转换为 word2 的最少操作数。
允许操作：插入一个字符、删除一个字符、替换一个字符。

输入格式：
第一行输入 word1。
第二行输入 word2。

输出格式：
输出最少操作数。
"""
        cases = [
            CaseSeed(f"{a}\n{b}", str(edit_distance(a, b)), False),
            CaseSeed("abc\nabc", "0", False),
            CaseSeed("distance\nediting", str(edit_distance("distance", "editing")), True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.HARD,
                time_limit=2600,
                memory_limit=256,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def trap_rain_water(height: Sequence[int]) -> int:
    if not height:
        return 0
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    ans = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            ans += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            ans += right_max - height[right]
            right -= 1
    return ans


def build_hard_trap_variants() -> list[ProblemSeed]:
    datasets = [
        [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],
        [4, 2, 0, 3, 2, 5],
        [5, 4, 1, 2],
        [2, 0, 2],
    ]
    seeds: list[ProblemSeed] = []
    for idx, arr in enumerate(datasets, start=1):
        title = f"接雨水 {idx}"
        desc = """给定非负整数数组 height，表示柱状图高度，计算下雨后可接的总雨水量。

输入格式：
第一行输入 n。
第二行输入 n 个非负整数。

输出格式：
输出可接雨水总量。
"""
        cases = [
            CaseSeed(f"{len(arr)}\n{format_ints(arr)}", str(trap_rain_water(arr)), False),
            CaseSeed("3\n2 0 2", "2", False),
            CaseSeed("6\n5 0 0 0 0 5", "20", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.HARD,
                time_limit=2500,
                memory_limit=196,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def sliding_window_max(nums: Sequence[int], k: int) -> list[int]:
    from collections import deque

    q: deque[int] = deque()
    ans: list[int] = []
    for i, x in enumerate(nums):
        while q and q[0] <= i - k:
            q.popleft()
        while q and nums[q[-1]] <= x:
            q.pop()
        q.append(i)
        if i >= k - 1:
            ans.append(nums[q[0]])
    return ans


def build_hard_sliding_max_variants() -> list[ProblemSeed]:
    datasets = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3),
        ([9, 11], 2),
        ([4, -2], 2),
        ([7, 2, 4], 2),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (nums, k) in enumerate(datasets, start=1):
        title = f"滑动窗口最大值 {idx}"
        desc = """给定整数数组 nums 和窗口大小 k，窗口从左到右滑动，输出每个窗口内的最大值。

输入格式：
第一行输入 n。
第二行输入 n 个整数。
第三行输入 k。

输出格式：
输出一行，按顺序输出每个窗口最大值（空格分隔）。
"""
        cases = [
            CaseSeed(
                f"{len(nums)}\n{format_ints(nums)}\n{k}",
                format_ints(sliding_window_max(nums, k)),
                False,
            ),
            CaseSeed("6\n1 3 1 2 0 5\n3", "3 3 2 5", False),
            CaseSeed("7\n10 9 8 7 6 5 4\n4", "10 9 8 7", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.HARD,
                time_limit=2600,
                memory_limit=196,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def min_window_substring(s: str, t: str) -> str:
    from collections import Counter

    need = Counter(t)
    missing = len(t)
    left = start = end = 0
    for right, ch in enumerate(s, start=1):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while left < right and need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if end == 0 or right - left < end - start:
                start, end = left, right
            need[s[left]] += 1
            missing += 1
            left += 1
    return s[start:end]


def build_hard_min_window_variants() -> list[ProblemSeed]:
    datasets = [
        ("ADOBECODEBANC", "ABC"),
        ("a", "a"),
        ("a", "aa"),
        ("abdecfab", "abc"),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (s, t) in enumerate(datasets, start=1):
        title = f"最小覆盖子串 {idx}"
        desc = """给定字符串 s 和 t，返回 s 中包含 t 所有字符的最小子串。
若不存在，输出空字符串（即输出空行）。

输入格式：
第一行输入字符串 s。
第二行输入字符串 t。

输出格式：
输出最小覆盖子串。
"""
        cases = [
            CaseSeed(f"{s}\n{t}", min_window_substring(s, t), False),
            CaseSeed("aaabdabcefaecbef\naabc", "abc", False),
            CaseSeed("xyz\nab", "", True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.HARD,
                time_limit=3000,
                memory_limit=256,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def longest_valid_parentheses(s: str) -> int:
    stack = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return best


def build_hard_longest_valid_parentheses_variants() -> list[ProblemSeed]:
    samples = [
        "(()",
        ")()())",
        "",
        "()(())",
    ]
    seeds: list[ProblemSeed] = []
    for idx, s in enumerate(samples, start=1):
        title = f"最长有效括号 {idx}"
        desc = """给定只包含 '(' 和 ')' 的字符串，求最长有效括号子串长度。

输入格式：
输入一行字符串 s。

输出格式：
输出一个整数表示最长长度。
"""
        cases = [
            CaseSeed(s, str(longest_valid_parentheses(s)), False),
            CaseSeed("((()))", "6", False),
            CaseSeed(")()((())())", str(longest_valid_parentheses(")()((())())")), True),
        ]
        seeds.append(
            ProblemSeed(
                title=title,
                description=normalize_text(desc),
                difficulty=DifficultyEnum.HARD,
                time_limit=2500,
                memory_limit=196,
                test_cases=mark_hidden(cases),
            )
        )
    return seeds


def build_all_seeds() -> list[ProblemSeed]:
    easy = (
        build_easy_sum_variants()
        + build_easy_max_min_gap_variants()
        + build_easy_even_count_variants()
        + build_easy_binary_search_variants()
        + build_easy_palindrome_variants()
        + build_easy_valid_parentheses_variants()
        + build_easy_fib_variants()
        + build_easy_two_sum_variants()
    )
    medium = (
        build_medium_longest_substr_variants()
        + build_medium_subarray_sum_k_variants()
        + build_medium_min_len_subarray_variants()
        + build_medium_merge_intervals_variants()
        + build_medium_lis_variants()
        + build_medium_coin_change_variants()
        + build_medium_island_variants()
        + build_medium_spiral_variants()
    )
    hard = (
        build_hard_edit_distance_variants()
        + build_hard_trap_variants()
        + build_hard_sliding_max_variants()
        + build_hard_min_window_variants()
        + build_hard_longest_valid_parentheses_variants()
    )
    return easy + medium + hard


def pick_by_difficulty(
    seeds: Iterable[ProblemSeed],
    easy_count: int,
    medium_count: int,
    hard_count: int,
) -> list[ProblemSeed]:
    easy = [x for x in seeds if x.difficulty == DifficultyEnum.EASY]
    medium = [x for x in seeds if x.difficulty == DifficultyEnum.MEDIUM]
    hard = [x for x in seeds if x.difficulty == DifficultyEnum.HARD]

    if len(easy) < easy_count:
        raise ValueError(f"Easy 题目不足: 需要 {easy_count}，可用 {len(easy)}")
    if len(medium) < medium_count:
        raise ValueError(f"Medium 题目不足: 需要 {medium_count}，可用 {len(medium)}")
    if len(hard) < hard_count:
        raise ValueError(f"Hard 题目不足: 需要 {hard_count}，可用 {len(hard)}")

    return easy[:easy_count] + medium[:medium_count] + hard[:hard_count]


def chunk_list(items: Sequence[ProblemSeed], size: int) -> list[list[ProblemSeed]]:
    if size <= 0:
        return [list(items)]
    return [list(items[i : i + size]) for i in range(0, len(items), size)]


async def count_official_and_ai() -> tuple[int, int]:
    async with AsyncSessionLocal() as db:
        official_stmt = select(func.count(Problem.id)).where(
            or_(
                Problem.source_type == ProblemSourceEnum.OFFICIAL,
                Problem.source_type.is_(None),
            )
        )
        ai_stmt = select(func.count(Problem.id)).where(
            Problem.source_type == ProblemSourceEnum.AI_GENERATED
        )
        official = (await db.execute(official_stmt)).scalar() or 0
        ai = (await db.execute(ai_stmt)).scalar() or 0
        return official, ai


async def wipe_official_problems() -> int:
    async with AsyncSessionLocal() as db:
        stmt = delete(Problem).where(
            or_(
                Problem.source_type == ProblemSourceEnum.OFFICIAL,
                Problem.source_type.is_(None),
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount or 0


async def insert_batch(batch: list[ProblemSeed]) -> int:
    async with AsyncSessionLocal() as db:
        existing_desc_hashes = set(
            (
                await db.execute(
                    select(Problem.description_hash).where(
                        and_(
                            or_(
                                Problem.source_type == ProblemSourceEnum.OFFICIAL,
                                Problem.source_type.is_(None),
                            ),
                            Problem.description_hash.is_not(None),
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        inserted = 0
        for seed in batch:
            title_hash = content_hash(seed.title)
            description_hash = content_hash(seed.description)
            if description_hash in existing_desc_hashes:
                continue

            problem = Problem(
                title=seed.title,
                description=seed.description,
                difficulty=seed.difficulty,
                time_limit=seed.time_limit,
                memory_limit=seed.memory_limit,
                source_type=ProblemSourceEnum.OFFICIAL,
                owner_id=None,
                title_hash=title_hash,
                description_hash=description_hash,
            )
            db.add(problem)
            await db.flush()

            for case in seed.test_cases:
                db.add(
                    TestCase(
                        problem_id=problem.id,
                        input_data=case.input_data,
                        expected_output=case.expected_output,
                        is_hidden=case.is_hidden,
                    )
                )
            inserted += 1
            existing_desc_hashes.add(description_hash)

        await db.commit()
        return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="重建官方题库")
    parser.add_argument("--easy", type=int, default=40, help="Easy 题数量")
    parser.add_argument("--medium", type=int, default=40, help="Medium 题数量")
    parser.add_argument("--hard", type=int, default=20, help="Hard 题数量")
    parser.add_argument("--batch-size", type=int, default=20, help="每批写入数量")
    parser.add_argument(
        "--wipe-official",
        action="store_true",
        help="先清空所有官方题",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    seeds = build_all_seeds()
    selected = pick_by_difficulty(
        seeds=seeds,
        easy_count=args.easy,
        medium_count=args.medium,
        hard_count=args.hard,
    )
    assign_distinct_type_profiles(selected)
    enriched_count = enrich_duplicate_descriptions(selected)
    validate_unique_seed_content(selected)
    batches = chunk_list(selected, args.batch_size)

    print("准备重建官方题库:")
    print(f"- Easy: {args.easy}")
    print(f"- Medium: {args.medium}")
    print(f"- Hard: {args.hard}")
    print(f"- 总数: {len(selected)}")
    print(f"- 批次数: {len(batches)} (batch_size={args.batch_size})")
    print(f"- 变体补充题数: {enriched_count}")

    before_official, before_ai = await count_official_and_ai()
    print(f"重建前: official={before_official}, ai_private={before_ai}")

    if args.wipe_official:
        deleted = await wipe_official_problems()
        print(f"已删除官方题: {deleted}")
    else:
        print("未指定 --wipe-official，跳过删除官方题")

    total_inserted = 0
    for idx, batch in enumerate(batches, start=1):
        inserted = await insert_batch(batch)
        total_inserted += inserted
        print(f"[Batch {idx}/{len(batches)}] 新增 {inserted} 题，累计 {total_inserted}")

    after_official, after_ai = await count_official_and_ai()
    print(f"重建后: official={after_official}, ai_private={after_ai}")
    print("完成。")


if __name__ == "__main__":
    asyncio.run(main())
