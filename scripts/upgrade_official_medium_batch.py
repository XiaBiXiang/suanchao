"""
中等题提质脚本（批量替换）

用途:
- 将官方题库中指定批次的 Medium 题替换为更高质量题面
- 不改变题库总量与难度分布，仅替换题面与测试用例内容

默认行为:
- 替换按创建时间升序的前 20 道 Medium 官方题
"""

from __future__ import annotations

import argparse
import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import and_, delete, or_, select

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
    time_limit: int
    memory_limit: int
    test_cases: list[CaseSeed]


def fmt_nums(nums: Sequence[int]) -> str:
    return " ".join(str(x) for x in nums)


def ensure_hidden(cases: list[CaseSeed]) -> list[CaseSeed]:
    if not any(case.is_hidden for case in cases):
        cases[-1].is_hidden = True
    return cases


def daily_temperatures(temps: Sequence[int]) -> list[int]:
    n = len(temps)
    ans = [0] * n
    stack: list[int] = []
    for i, t in enumerate(temps):
        while stack and t > temps[stack[-1]]:
            prev = stack.pop()
            ans[prev] = i - prev
        stack.append(i)
    return ans


def build_daily_temp_seeds() -> list[ProblemSeed]:
    datasets = [
        [73, 74, 75, 71, 69, 72, 76, 73],
        [30, 40, 50, 60],
        [30, 60, 90],
        [90, 80, 70, 60],
        [65, 62, 70, 60, 75, 72, 80],
    ]
    seeds: list[ProblemSeed] = []
    for idx, temps in enumerate(datasets, start=1):
        cases = ensure_hidden(
            [
                CaseSeed(
                    f"{len(temps)}\n{fmt_nums(temps)}",
                    fmt_nums(daily_temperatures(temps)),
                    False,
                ),
                CaseSeed("6\n60 61 62 59 70 72", "1 1 2 1 1 0", False),
                CaseSeed("7\n80 79 78 77 76 75 74", "0 0 0 0 0 0 0", True),
            ]
        )
        seeds.append(
            ProblemSeed(
                title=f"单调栈·每日温度 {idx}",
                description=(
                    "给定每日气温数组，输出每一天距离下一次更高气温还需等待多少天。\n\n"
                    "输入格式：\n"
                    "第一行输入整数 n。\n"
                    "第二行输入 n 个整数，表示每日气温。\n\n"
                    "输出格式：\n"
                    "输出 n 个整数（空格分隔），第 i 个值表示第 i 天后首次升温的间隔天数；若之后不会升温，输出 0。\n\n"
                    "数据范围：\n"
                    "- 1 <= n <= 2 * 10^5\n"
                    "- -50 <= temperature <= 150"
                ),
                time_limit=2000,
                memory_limit=196,
                test_cases=cases,
            )
        )
    return seeds


def search_rotated(nums: Sequence[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def build_rotated_search_seeds() -> list[ProblemSeed]:
    datasets = [
        ([4, 5, 6, 7, 0, 1, 2], 0),
        ([4, 5, 6, 7, 0, 1, 2], 3),
        ([1], 0),
        ([5, 1, 3], 5),
        ([6, 7, 8, 1, 2, 3, 4, 5], 3),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (nums, target) in enumerate(datasets, start=1):
        cases = ensure_hidden(
            [
                CaseSeed(
                    f"{len(nums)}\n{fmt_nums(nums)}\n{target}",
                    str(search_rotated(nums, target)),
                    False,
                ),
                CaseSeed("7\n9 10 11 12 1 3 5\n3", "5", False),
                CaseSeed("8\n15 16 19 20 1 3 5 7\n17", "-1", True),
            ]
        )
        seeds.append(
            ProblemSeed(
                title=f"二分·旋转数组搜索 {idx}",
                description=(
                    "给定一个严格升序数组经过一次旋转后的结果 nums（元素互不重复），以及目标值 target，"
                    "请返回 target 的下标，若不存在则返回 -1。\n\n"
                    "输入格式：\n"
                    "第一行输入 n。\n"
                    "第二行输入 n 个整数 nums。\n"
                    "第三行输入 target。\n\n"
                    "输出格式：\n"
                    "输出一个整数下标。\n\n"
                    "要求时间复杂度尽量接近 O(log n)。"
                ),
                time_limit=1800,
                memory_limit=128,
                test_cases=cases,
            )
        )
    return seeds


def min_jumps(nums: Sequence[int]) -> int:
    if len(nums) <= 1:
        return 0
    steps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:
            steps += 1
            current_end = farthest
    return steps


def build_jump_game_seeds() -> list[ProblemSeed]:
    datasets = [
        [2, 3, 1, 1, 4],
        [2, 3, 0, 1, 4],
        [1, 1, 1, 1, 1],
        [4, 1, 1, 3, 1, 1, 1],
        [2, 1, 2, 3, 1, 1, 1],
    ]
    seeds: list[ProblemSeed] = []
    for idx, nums in enumerate(datasets, start=1):
        cases = ensure_hidden(
            [
                CaseSeed(f"{len(nums)}\n{fmt_nums(nums)}", str(min_jumps(nums)), False),
                CaseSeed("6\n1 2 1 1 1 1", "4", False),
                CaseSeed("8\n3 4 2 1 2 1 5 1", "3", True),
            ]
        )
        seeds.append(
            ProblemSeed(
                title=f"贪心·最少跳跃次数 {idx}",
                description=(
                    "给定非负整数数组 nums，初始位于下标 0。nums[i] 表示从位置 i 最多可向前跳的步数。"
                    "请计算到达最后一个下标的最少跳跃次数。\n\n"
                    "输入保证总能到达最后位置。\n\n"
                    "输入格式：\n"
                    "第一行输入 n。\n"
                    "第二行输入 n 个整数 nums。\n\n"
                    "输出格式：\n"
                    "输出一个整数，表示最少跳跃次数。"
                ),
                time_limit=1800,
                memory_limit=128,
                test_cases=cases,
            )
        )
    return seeds


def can_finish_courses(course_count: int, edges: Sequence[tuple[int, int]]) -> bool:
    graph = [[] for _ in range(course_count)]
    indegree = [0] * course_count
    for nxt, pre in edges:
        graph[pre].append(nxt)
        indegree[nxt] += 1

    queue = deque([i for i in range(course_count) if indegree[i] == 0])
    taken = 0
    while queue:
        cur = queue.popleft()
        taken += 1
        for nxt in graph[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return taken == course_count


def edges_to_input(course_count: int, edges: Sequence[tuple[int, int]]) -> str:
    lines = [f"{course_count} {len(edges)}"]
    lines.extend(f"{a} {b}" for a, b in edges)
    return "\n".join(lines)


def build_course_schedule_seeds() -> list[ProblemSeed]:
    datasets = [
        (2, [(1, 0)]),
        (2, [(1, 0), (0, 1)]),
        (4, [(1, 0), (2, 0), (3, 1), (3, 2)]),
        (5, [(1, 0), (2, 1), (3, 2), (1, 3)]),
        (6, [(1, 0), (2, 0), (3, 1), (4, 2), (5, 3)]),
    ]
    seeds: list[ProblemSeed] = []
    for idx, (n, edges) in enumerate(datasets, start=1):
        cases = ensure_hidden(
            [
                CaseSeed(
                    edges_to_input(n, edges),
                    "Yes" if can_finish_courses(n, edges) else "No",
                    False,
                ),
                CaseSeed("3 2\n1 0\n2 1", "Yes", False),
                CaseSeed("4 4\n1 0\n2 1\n3 2\n1 3", "No", True),
            ]
        )
        seeds.append(
            ProblemSeed(
                title=f"图论·课程安排可行性 {idx}",
                description=(
                    "共有 n 门课程，编号为 0 ~ n-1。给定若干先修关系 [a, b]，表示学习 a 前必须先学 b。"
                    "请判断是否可以完成全部课程。\n\n"
                    "输入格式：\n"
                    "第一行输入 n 和 m，分别表示课程数与关系数。\n"
                    "接下来 m 行，每行两个整数 a b。\n\n"
                    "输出格式：\n"
                    "若可完成输出 Yes，否则输出 No。"
                ),
                time_limit=2200,
                memory_limit=196,
                test_cases=cases,
            )
        )
    return seeds


def build_seed_pool() -> list[ProblemSeed]:
    return (
        build_daily_temp_seeds()
        + build_rotated_search_seeds()
        + build_jump_game_seeds()
        + build_course_schedule_seeds()
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量替换 Medium 官方题")
    parser.add_argument("--offset", type=int, default=0, help="从第几道 Medium 官方题开始替换")
    parser.add_argument("--count", type=int, default=20, help="替换数量（最大 20）")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写入")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise ValueError("--count 必须大于 0")

    seed_pool = build_seed_pool()
    if args.count > len(seed_pool):
        raise ValueError(f"--count 最大为 {len(seed_pool)}")

    seeds = seed_pool[: args.count]
    official_cond = or_(
        Problem.source_type == ProblemSourceEnum.OFFICIAL,
        Problem.source_type.is_(None),
    )

    async with AsyncSessionLocal() as db:
        problem_stmt = (
            select(Problem)
            .where(and_(official_cond, Problem.difficulty == DifficultyEnum.MEDIUM))
            .order_by(Problem.created_at.asc())
            .offset(args.offset)
            .limit(args.count)
        )
        targets = list((await db.execute(problem_stmt)).scalars().all())
        if len(targets) < args.count:
            raise ValueError(
                f"可替换 Medium 题不足: 需要 {args.count}，实际 {len(targets)}"
            )

        print(f"将替换 Medium 官方题 {args.count} 道（offset={args.offset}）")
        for i, (problem, seed) in enumerate(zip(targets, seeds), start=1):
            print(f"{i:02d}. {problem.title}  ->  {seed.title}")

        if args.dry_run:
            print("dry-run 模式：未写入数据库")
            return

        for problem, seed in zip(targets, seeds):
            problem.title = seed.title
            problem.description = seed.description
            problem.difficulty = DifficultyEnum.MEDIUM
            problem.time_limit = seed.time_limit
            problem.memory_limit = seed.memory_limit
            problem.source_type = ProblemSourceEnum.OFFICIAL
            problem.owner_id = None

            await db.execute(delete(TestCase).where(TestCase.problem_id == problem.id))
            for case in seed.test_cases:
                db.add(
                    TestCase(
                        problem_id=problem.id,
                        input_data=case.input_data,
                        expected_output=case.expected_output,
                        is_hidden=case.is_hidden,
                    )
                )

        await db.commit()
        print("写入完成。")


if __name__ == "__main__":
    asyncio.run(main())
