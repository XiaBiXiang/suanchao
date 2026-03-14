"""
判题服务模块
使用 Docker/Podman 沙箱安全执行用户代码
"""

import asyncio
import subprocess
import re
import base64
import time
from typing import Awaitable, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class JudgeStatus(str, Enum):
    AC = "AC"
    WA = "WA"
    TLE = "TLE"
    MLE = "MLE"
    RE = "RE"
    CE = "CE"
    SYSTEM_ERROR = "SYSTEM_ERROR"


@dataclass
class TestCaseResult:
    test_case_id: str
    status: str
    input_data: str
    expected_output: str
    actual_output: str
    execution_time_ms: Optional[int] = None
    memory_used_mb: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class JudgeResult:
    status: str
    total_cases: int
    passed_cases: int
    total_time_ms: int
    max_memory_mb: int
    test_results: List[TestCaseResult]
    message: str


ProgressCallback = Optional[Callable[[int, str], Awaitable[None] | None]]


class JudgeService:
    BASE_IMAGE = "python:3.9-alpine"
    RUNTIME = "/opt/podman/bin/podman"

    def __init__(self):
        self.client = None

    async def run_code_in_sandbox(
        self,
        code: str,
        test_cases: List[Dict],
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128,
        language: str = "python",
        progress_callback: ProgressCallback = None,
    ) -> JudgeResult:
        test_results = []
        passed_cases = 0
        total_time = 0
        max_memory = 0
        final_status = JudgeStatus.AC
        total_cases = max(1, len(test_cases))

        await self._emit_progress(progress_callback, 6, "判题任务开始执行")

        for index, test_case in enumerate(test_cases):
            result = await self._run_single_test(
                code=code,
                input_data=test_case.get("input_data", ""),
                expected_output=test_case.get("expected_output", ""),
                test_case_id=test_case.get("id", ""),
                time_limit_ms=time_limit_ms,
                memory_limit_mb=memory_limit_mb,
                language=language,
            )

            test_results.append(result)
            total_time += result.execution_time_ms or 0
            max_memory = max(max_memory, result.memory_used_mb or 0)

            if result.status == JudgeStatus.AC:
                passed_cases += 1
            elif result.status == JudgeStatus.TLE:
                final_status = JudgeStatus.TLE
                break
            elif result.status == JudgeStatus.MLE:
                final_status = JudgeStatus.MLE
                break
            elif result.status == JudgeStatus.RE:
                final_status = JudgeStatus.RE
                break
            elif result.status == JudgeStatus.WA:
                if final_status == JudgeStatus.AC:
                    final_status = JudgeStatus.WA

            progress = min(95, int(((index + 1) / total_cases) * 90) + 5)
            await self._emit_progress(
                progress_callback,
                progress,
                f"正在执行测试用例 {index + 1}/{total_cases}",
            )

        if final_status == JudgeStatus.AC:
            if passed_cases == len(test_cases):
                message = "所有测试用例通过"
            else:
                message = f"{passed_cases}/{len(test_cases)} 测试用例通过"
        elif final_status == JudgeStatus.WA:
            message = f"{passed_cases}/{len(test_cases)} 测试用例通过"
        elif final_status == JudgeStatus.TLE:
            message = "执行超时 (Time Limit Exceeded)"
        elif final_status == JudgeStatus.MLE:
            message = "内存超限 (Memory Limit Exceeded)"
        elif final_status == JudgeStatus.RE:
            message = "运行时错误 (Runtime Error)"
        else:
            message = "未知错误"

        await self._emit_progress(progress_callback, 100, "判题执行完成")

        return JudgeResult(
            status=final_status,
            total_cases=len(test_cases),
            passed_cases=passed_cases,
            total_time_ms=total_time,
            max_memory_mb=max_memory,
            test_results=test_results,
            message=message,
        )

    async def run_with_custom_input(
        self,
        code: str,
        custom_input: str,
        time_limit_ms: int = 1000,
        memory_limit_mb: int = 128,
        language: str = "python",
        progress_callback: ProgressCallback = None,
    ) -> JudgeResult:
        await self._emit_progress(progress_callback, 8, "开始运行自定义输入")

        if language == "python":
            run_cmd = self._build_python_script_cmd(code, custom_input)
        else:
            run_cmd = f'echo "{code}"'

        try:
            timeout_seconds = max(1, (time_limit_ms // 1000) + 1)
            start_time = time.perf_counter()
            result = await asyncio.to_thread(
                self._execute_container_cmd,
                run_cmd,
                memory_limit_mb,
                timeout_seconds,
            )
            execution_time_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            await self._emit_progress(progress_callback, 90, "已完成代码执行，正在整理输出")

            if result.returncode != 0:
                error_msg = (
                    result.stderr.strip()
                    if result.stderr
                    else f"进程退出码: {result.returncode}"
                )
                await self._emit_progress(progress_callback, 100, "运行失败")
                return JudgeResult(
                    status=JudgeStatus.RE,
                    total_cases=1,
                    passed_cases=0,
                    total_time_ms=execution_time_ms,
                    max_memory_mb=0,
                    test_results=[
                        TestCaseResult(
                            test_case_id="custom-input",
                            status=JudgeStatus.RE,
                            input_data=custom_input,
                            expected_output="",
                            actual_output="",
                            execution_time_ms=execution_time_ms,
                            error_message=error_msg,
                        )
                    ],
                    message="运行时错误 (Runtime Error)",
                )

            actual_output = (result.stdout or "").strip()
            await self._emit_progress(progress_callback, 100, "运行完成")
            return JudgeResult(
                status=JudgeStatus.AC,
                total_cases=1,
                passed_cases=1,
                total_time_ms=execution_time_ms,
                max_memory_mb=0,
                test_results=[
                    TestCaseResult(
                        test_case_id="custom-input",
                        status=JudgeStatus.AC,
                        input_data=custom_input,
                        expected_output="",
                        actual_output=actual_output,
                        execution_time_ms=execution_time_ms,
                    )
                ],
                message="运行完成",
            )
        except subprocess.TimeoutExpired:
            await self._emit_progress(progress_callback, 100, "运行超时")
            return JudgeResult(
                status=JudgeStatus.TLE,
                total_cases=1,
                passed_cases=0,
                total_time_ms=time_limit_ms,
                max_memory_mb=0,
                test_results=[
                    TestCaseResult(
                        test_case_id="custom-input",
                        status=JudgeStatus.TLE,
                        input_data=custom_input,
                        expected_output="",
                        actual_output="",
                        execution_time_ms=time_limit_ms,
                        error_message="执行超时",
                    )
                ],
                message="执行超时 (Time Limit Exceeded)",
            )
        except Exception as exc:
            await self._emit_progress(progress_callback, 100, "运行异常")
            return JudgeResult(
                status=JudgeStatus.SYSTEM_ERROR,
                total_cases=1,
                passed_cases=0,
                total_time_ms=0,
                max_memory_mb=0,
                test_results=[
                    TestCaseResult(
                        test_case_id="custom-input",
                        status=JudgeStatus.SYSTEM_ERROR,
                        input_data=custom_input,
                        expected_output="",
                        actual_output="",
                        error_message=f"执行异常: {str(exc)}",
                    )
                ],
                message="系统异常",
            )

    async def _run_single_test(
        self,
        code: str,
        input_data: str,
        expected_output: str,
        test_case_id: str,
        time_limit_ms: int,
        memory_limit_mb: int,
        language: str,
    ) -> TestCaseResult:
        if language == "python":
            # 优先以标准输入脚本模式执行，兼容题目“输入/输出”格式
            run_cmd = self._build_python_script_cmd(code, input_data)
        else:
            run_cmd = f'echo "{code}"'

        try:
            timeout_seconds = max(1, (time_limit_ms // 1000) + 1)

            start_time = time.perf_counter()
            result = await asyncio.to_thread(
                self._execute_container_cmd,
                run_cmd,
                memory_limit_mb,
                timeout_seconds,
            )
            execution_time_ms = max(
                1,
                int((time.perf_counter() - start_time) * 1000),
            )

            # 脚本模式无输出且期望非空时，回退到函数调用模式，兼容旧题与函数式写法
            if language == "python":
                expected_clean = expected_output.strip()
                actual_clean = result.stdout.strip()
                if result.returncode == 0 and not actual_clean and expected_clean:
                    fallback_cmd = self._wrap_python_code(code, input_data)
                    fallback_start_time = time.perf_counter()
                    fallback_result = await asyncio.to_thread(
                        self._execute_container_cmd,
                        fallback_cmd,
                        memory_limit_mb,
                        timeout_seconds,
                    )
                    execution_time_ms += max(
                        1,
                        int((time.perf_counter() - fallback_start_time) * 1000),
                    )
                    # 仅在回退得到非空输出或报错时替换，避免吞掉脚本模式的空输出场景
                    if fallback_result.returncode != 0 or fallback_result.stdout.strip():
                        result = fallback_result

            actual_output = result.stdout.strip()
            expected_clean = expected_output.strip()

            if result.returncode != 0:
                error_msg = (
                    result.stderr.strip()
                    if result.stderr
                    else f"进程退出码: {result.returncode}"
                )
                return TestCaseResult(
                    test_case_id=test_case_id,
                    status=JudgeStatus.RE,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output="",
                    execution_time_ms=execution_time_ms,
                    error_message=error_msg,
                )

            if actual_output == expected_clean:
                return TestCaseResult(
                    test_case_id=test_case_id,
                    status=JudgeStatus.AC,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    execution_time_ms=execution_time_ms,
                )
            else:
                return TestCaseResult(
                    test_case_id=test_case_id,
                    status=JudgeStatus.WA,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    execution_time_ms=execution_time_ms,
                )

        except subprocess.TimeoutExpired:
            return TestCaseResult(
                test_case_id=test_case_id,
                status=JudgeStatus.TLE,
                input_data=input_data,
                expected_output=expected_output,
                actual_output="",
                execution_time_ms=time_limit_ms,
                error_message="执行超时",
            )

        except Exception as e:
            return TestCaseResult(
                test_case_id=test_case_id,
                status=JudgeStatus.SYSTEM_ERROR,
                input_data=input_data,
                expected_output=expected_output,
                actual_output="",
                error_message=f"执行异常: {str(e)}",
            )

    def _execute_container_cmd(
        self,
        run_cmd: str,
        memory_limit_mb: int,
        timeout_seconds: int,
    ) -> subprocess.CompletedProcess:
        cmd = [
            self.RUNTIME,
            "run",
            "--rm",
            "-m",
            f"{memory_limit_mb}m",
            "--network",
            "none",
            "--read-only",
            "--pids-limit",
            "50",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            self.BASE_IMAGE,
            "sh",
            "-c",
            run_cmd,
        ]
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

    def _build_python_script_cmd(self, code: str, input_data: str) -> str:
        code_b64 = base64.b64encode(code.encode()).decode()
        input_b64 = base64.b64encode(input_data.encode()).decode()
        return (
            f"echo {code_b64} | base64 -d > /tmp/j.py && "
            f"echo {input_b64} | base64 -d > /tmp/in.txt && "
            "python3 /tmp/j.py < /tmp/in.txt"
        )

    def _wrap_python_code(self, code: str, input_data: str) -> str:
        lines = code.split("\n")
        func_name = "solution"
        has_listnode = "ListNode" in code
        in_class = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("class "):
                in_class = True
            elif in_class and stripped and not stripped.startswith("#"):
                if stripped.startswith("def "):
                    continue
                if not stripped.startswith(" ") and not stripped.startswith("\t"):
                    in_class = False
            elif not in_class and stripped.startswith("def "):
                match = re.match(r"def\s+(\w+)\s*\(", stripped)
                if match:
                    func_name = match.group(1)
                    break

        input_lines = input_data.strip().split("\n")
        input_repr = "[" + ",".join([repr(line) for line in input_lines]) + "]"

        # 只在函数名以 list 结尾时使用链表（排除 solution）
        use_ll = has_listnode or (
            func_name.lower().endswith("list") and func_name.lower() != "solution"
        )
        use_ll_str = "True" if use_ll else "False"

        # 构建代码模板
        wrapper = f'''import sys
import re
import io
import inspect

{code}

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def list_to_linkedlist(lst):
    if not lst:
        return None
    dummy = ListNode(0)
    curr = dummy
    for val in lst:
        curr.next = ListNode(val)
        curr = curr.next
    return dummy.next

def linkedlist_to_list(node):
    result = []
    while node:
        result.append(node.val)
        node = node.next
    return result

input_lines = {input_repr}
sys.stdin = io.StringIO("\\n".join(input_lines))
args = []
for line in input_lines:
    try:
        parsed = eval(line)
        if isinstance(parsed, list):
            if {use_ll_str}:
                args.append(list_to_linkedlist(parsed))
            else:
                args.append(parsed)
        else:
            args.append(parsed)
    except:
        try:
            nums = re.findall(r"-?\\d+", line)
            if len(nums) > 1:
                if {use_ll_str}:
                    args.append(list_to_linkedlist([int(x) for x in nums]))
                else:
                    args.append([int(x) for x in nums])
            else:
                args.append(int(line))
        except:
            args.append(line)

func = globals().get("{func_name}")
if func is None:
    print("__JUDGE_FUNCTION_NOT_FOUND__")
else:
    try:
        signature = inspect.signature(func)
        parameters = list(signature.parameters.values())
        positional = [
            p for p in parameters
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        required = [p for p in positional if p.default is inspect.Parameter.empty]
        has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in parameters)

        if len(required) == 0 and not has_varargs:
            result = func()
        elif has_varargs:
            result = func(*args)
        else:
            result = func(*args[:len(positional)])

        if result is None:
            pass
        elif isinstance(result, ListNode):
            print(" ".join(map(str, linkedlist_to_list(result))))
        elif isinstance(result, (list, tuple)):
            print(" ".join(map(str, result)))
        else:
            print(result)
    except Exception as e:
        print("ERROR:" + str(e))
'''

        # 使用 base64 传递代码
        code_b64 = base64.b64encode(wrapper.encode()).decode()
        return f"echo {code_b64} | base64 -d > /tmp/j.py && python3 /tmp/j.py"

    async def _emit_progress(
        self,
        progress_callback: ProgressCallback,
        progress: int,
        message: str,
    ) -> None:
        if progress_callback is None:
            return
        maybe_awaitable = progress_callback(progress, message)
        if asyncio.iscoroutine(maybe_awaitable):
            await maybe_awaitable


judge_service = JudgeService()


async def run_code_in_sandbox(
    code: str,
    test_cases: List[Dict],
    time_limit_ms: int = 1000,
    memory_limit_mb: int = 128,
    language: str = "python",
    progress_callback: ProgressCallback = None,
) -> JudgeResult:
    return await judge_service.run_code_in_sandbox(
        code, test_cases, time_limit_ms, memory_limit_mb, language, progress_callback
    )


async def run_custom_input_in_sandbox(
    code: str,
    custom_input: str,
    time_limit_ms: int = 1000,
    memory_limit_mb: int = 128,
    language: str = "python",
    progress_callback: ProgressCallback = None,
) -> JudgeResult:
    return await judge_service.run_with_custom_input(
        code,
        custom_input,
        time_limit_ms,
        memory_limit_mb,
        language,
        progress_callback,
    )
