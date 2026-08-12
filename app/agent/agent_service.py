from typing import Any
from uuid import uuid4

from app.agent.workflow import (
    budget_agent_graph,
)
from langgraph.types import Command
import logging
import time
logger = logging.getLogger(
    __name__
)

def extract_interrupt_payload(
    result: dict[str, Any],
) -> Any | None:
    """从LangGraph结果中提取人工确认请求。"""

    interrupts = result.get(
        "__interrupt__",
        [],
    )

    if not interrupts:
        return None

    first_interrupt = interrupts[0]

    if hasattr(
        first_interrupt,
        "value",
    ):
        return first_interrupt.value

    return first_interrupt
def run_budget_agent(
    user_input: str,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """运行一次BudgetPilot Agent会话。"""

    cleaned_input = user_input.strip()

    if not cleaned_input:
        raise ValueError(
            "用户输入不能为空"
        )

    # 防止前端误传字符串 "null"
    normalized_thread_id = thread_id

    if normalized_thread_id is not None:
        normalized_thread_id = (
            normalized_thread_id.strip()
        )

        if normalized_thread_id.lower() in {
            "",
            "null",
            "none",
        }:
            normalized_thread_id = None

    current_thread_id = (
        normalized_thread_id
        or str(uuid4())
    )

    start_time = time.perf_counter()

    logger.info(
        (
            "event=agent_start "
            f"thread_id={current_thread_id}"
        )
    )

    config = {
        "configurable": {
            "thread_id": current_thread_id,
        }
    }

    result = budget_agent_graph.invoke(
        {
            "user_input": cleaned_input,
        },
        config=config,
    )

    # ============================
    # 1. 检查是否被interrupt暂停
    # ============================

    interrupt_payload = (
        extract_interrupt_payload(
            result
        )
    )

    if interrupt_payload is not None:

        if isinstance(
            interrupt_payload,
            dict,
        ):
            approval_message = (
                interrupt_payload.get(
                    "message",
                    "当前操作需要人工确认。",
                )
            )

        else:
            approval_message = str(
                interrupt_payload
            )

        elapsed_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        logger.info(
            (
                "event=agent_interrupted "
                f"thread_id={current_thread_id} "
                f"intent={result.get('intent')} "
                f"duration_ms={elapsed_ms:.2f}"
            )
        )

        # 注意：
        # interrupt以后直接return
        # 绝不能继续执行下面的completed逻辑
        return {
            "thread_id": current_thread_id,

            "status": (
                "waiting_for_approval"
            ),

            "requires_approval": True,

            "approval_request": (
                interrupt_payload
            ),

            "answer": approval_message,

            "intent": result.get(
                "intent",
                "budget_report",
            ),

            "routing_source": result.get(
                "routing_source",
            ),

            "route_reason": result.get(
                "route_reason",
            ),

            "department_id": result.get(
                "department_id",
            ),

            "month": result.get(
                "month",
            ),

            "trace": result.get(
                "trace",
                [],
            ),

            "details": None,
        }

    # ============================
    # 2. Graph正常执行完成
    # ============================

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    logger.info(
        (
            "event=agent_completed "
            f"thread_id={current_thread_id} "
            f"intent={result.get('intent')} "
            f"routing_source="
            f"{result.get('routing_source')} "
            f"duration_ms={elapsed_ms:.2f}"
        )
    )

    return {
        "thread_id": current_thread_id,

        "status": "completed",

        "requires_approval": False,

        "approval_request": None,

        "answer": result.get(
            "response",
            "Agent未生成有效回答。",
        ),

        "intent": result.get(
            "intent",
            "unknown",
        ),

        "routing_source": result.get(
            "routing_source",
        ),

        "route_reason": result.get(
            "route_reason",
        ),

        "department_id": result.get(
            "department_id",
        ),

        "month": result.get(
            "month",
        ),

        "trace": result.get(
            "trace",
            [],
        ),

        "details": result.get(
            "tool_result",
        ),
    }
def resume_budget_agent(
    thread_id: str,
    approved: bool,
) -> dict[str, Any]:
    """恢复正在等待人工确认的Agent任务。"""

    cleaned_thread_id = thread_id.strip()

    if not cleaned_thread_id:
        raise ValueError(
            "thread_id不能为空"
        )

    config = {
        "configurable": {
            "thread_id": cleaned_thread_id,
        }
    }

    # 先检查这个thread_id是否真的存在
    snapshot = budget_agent_graph.get_state(
        config
    )

    if not snapshot.values:
        raise ValueError(
            "未找到对应的Agent会话"
        )

    # 会话存在，但当前没有等待审批的interrupt
    if not snapshot.interrupts:
        raise ValueError(
            "该会话当前没有等待人工确认的任务"
        )

    start_time = time.perf_counter()

    logger.info(
        (
            "event=agent_resume_start "
            f"thread_id={cleaned_thread_id} "
            f"approved={approved}"
        )
    )

    result = budget_agent_graph.invoke(
        Command(
            resume=approved
        ),
        config=config,
    )

    interrupt_payload = (
        extract_interrupt_payload(
            result
        )
    )

    # 理论上当前流程只有一次审批，
    # 但保留再次暂停的处理能力。
    if interrupt_payload is not None:
        return {
            "thread_id": cleaned_thread_id,
            "status": "waiting_for_approval",
            "requires_approval": True,
            "approval_request": interrupt_payload,
            "answer": "任务仍在等待人工确认。",
            "intent": result.get(
                "intent",
                "unknown",
            ),
            "routing_source": result.get(
                "routing_source",
            ),
            "route_reason": result.get(
                "route_reason",
            ),
            "department_id": result.get(
                "department_id",
            ),
            "month": result.get(
                "month",
            ),
            "trace": result.get(
                "trace",
                [],
            ),
            "details": None,
        }

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    logger.info(
        (
            "event=agent_resume_completed "
            f"thread_id={cleaned_thread_id} "
            f"approved={approved} "
            f"intent={result.get('intent')} "
            f"duration_ms={elapsed_ms:.2f}"
        )
    )

    return {
        "thread_id": cleaned_thread_id,
        "status": "completed",
        "requires_approval": False,
        "approval_request": None,
        "answer": result.get(
            "response",
            "Agent未生成有效回答。",
        ),
        "intent": result.get(
            "intent",
            "unknown",
        ),
        "routing_source": result.get(
            "routing_source",
        ),
        "route_reason": result.get(
            "route_reason",
        ),
        "department_id": result.get(
            "department_id",
        ),
        "month": result.get(
            "month",
        ),
        "trace": result.get(
            "trace",
            [],
        ),
        "details": result.get(
            "tool_result",
        ),
    }
def run_memory_demo() -> None:
    """测试同一thread_id下的短期记忆。"""

    print("===== 第一轮 =====")

    first_result = run_budget_agent(
        "帮我看看研发部2026-07的预算执行情况"
    )

    print(
        "thread_id：",
        first_result["thread_id"],
    )
    print(
        "intent：",
        first_result["intent"],
    )
    print(
        "department_id：",
        first_result["department_id"],
    )
    print(
        "month：",
        first_result["month"],
    )
    print(
        "answer：",
        first_result["answer"],
    )

    # 最关键：
    # 第二轮复用第一轮的thread_id。
    same_thread_id = (
        first_result["thread_id"]
    )

    print("\n===== 第二轮 =====")

    second_result = run_budget_agent(
        "那风险呢？",
        thread_id=same_thread_id,
    )

    print(
        "thread_id：",
        second_result["thread_id"],
    )
    print(
        "intent：",
        second_result["intent"],
    )
    print(
        "department_id：",
        second_result["department_id"],
    )
    print(
        "month：",
        second_result["month"],
    )
    print(
        "answer：",
        second_result["answer"],
    )
    print(
        "trace：",
        second_result["trace"],
    )

def run_hitl_demo() -> None:
    """测试预算报告人工确认流程。"""

    print(
        "===== 第一步：请求生成报告 ====="
    )

    first_result = run_budget_agent(
        "帮我生成研发部2026-07的预算报告"
    )

    print(
        "thread_id：",
        first_result["thread_id"],
    )

    print(
        "status：",
        first_result["status"],
    )

    print(
        "requires_approval：",
        first_result[
            "requires_approval"
        ],
    )

    print(
        "approval_request：",
        first_result[
            "approval_request"
        ],
    )

    # 必须复用同一个thread_id
    thread_id = (
        first_result["thread_id"]
    )

    print(
        "\n===== 第二步：用户批准 ====="
    )

    second_result = (
        resume_budget_agent(
            thread_id=thread_id,
            approved=True,
        )
    )

    print(
        "status：",
        second_result["status"],
    )

    print(
        "requires_approval：",
        second_result[
            "requires_approval"
        ],
    )

    print(
        "answer：",
        second_result["answer"],
    )


if __name__ == "__main__":
    run_hitl_demo()
if __name__ == "__main__":
    run_memory_demo()