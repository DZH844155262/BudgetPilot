import json
import os
import re
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.agent.state import AgentIntent
from app.budget_service import get_departments
from app.rag.llm_client import get_llm_client
from app.agent.skill_registry import (
    load_skill_metadata,
)

DEFAULT_ROUTER_MODEL = os.getenv(
    "LLM_MODEL",
    "deepseek-v4-flash",
)


class RoutingDecision(BaseModel):
    """LLM输出的结构化路由结果。"""

    intent: AgentIntent = Field(
        description=(
           "用户意图，只允许为budget_analysis、"
        "risk_overview、policy_question、"
        "budget_report或unknown"
        ),
    )

    department_id: str | None = Field(
        default=None,
        pattern=r"^D\d{3}$",
        description=(
            "部门编号，例如D001；"
            "问题不涉及部门或无法确定时为null"
        ),
    )

    month: str | None = Field(
        default=None,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description=(
            "查询月份，格式为YYYY-MM；"
            "不涉及月份或无法确定时为null"
        ),
    )

    growth_threshold: float | None = Field(
        default=None,
        ge=0,
        description=(
            "用户明确指定的环比增长阈值；"
            "未指定时为null"
        ),
    )

    large_expense_threshold: float | None = Field(
        default=None,
        ge=0,
        description=(
            "用户明确指定的大额费用阈值；"
            "未指定时为null"
        ),
    )
    skill_name: str | None = Field(
    default=None,
    description=(
        "需要激活的Skill名称；"
        "当前仅允许budget-risk-review，"
        "不需要Skill时为null"
    ),
)
    reason: str = Field(
        min_length=1,
        max_length=200,
        description="简要说明路由原因",
    )


def get_valid_department_ids(
    departments: list[dict[str, Any]],
) -> set[str]:
    """从部门数据中提取合法部门编号。"""

    valid_ids: set[str] = set()

    for department in departments:
        for value in department.values():
            normalized_value = str(value).upper()

            if re.fullmatch(
                r"D\d{3}",
                normalized_value,
            ):
                valid_ids.add(normalized_value)

    return valid_ids


def build_router_system_prompt(
    departments: ...
) -> str:

    skill_metadata = load_skill_metadata(
        "budget-risk-review"
    )

    available_skill = (
        f"name: {skill_metadata['name']}\n"
        f"description: "
        f"{skill_metadata['description']}"
    )
    """构建Agent路由系统提示词。"""

    current_date = date.today().isoformat()

    department_json = json.dumps(
        departments,
        ensure_ascii=False,
        default=str,
    )

    return f"""
你是BudgetPilot企业预算助手的路由器。

你的任务不是回答用户问题，也不能执行任何业务操作。
你只负责识别用户意图并提取结构化参数。

当前日期：
{current_date}

当前可用部门：
{department_json}

意图分类规则：

1. budget_analysis
查询预算金额、实际支出、执行率、剩余额度、
费用使用情况等预算执行信息。

2. risk_overview
查询风险、异常、大额费用、环比增长、
超预算预警或需要重点关注的问题。

3. policy_question
询问企业制度、报销规定、审批流程、
需要提交的材料、金额门槛或制度要求。

4. budget_report
用户明确要求生成、制作、输出某部门某月份的
预算报告、预算分析报告或风险报告。

5. unknown
不属于以上四类，例如天气、闲聊和其他无关问题。

参数提取规则：

1. department_id只能从当前可用部门中选择。
2. 如果用户说部门名称，应根据部门列表转换成部门编号。
3. 月份必须转换成YYYY-MM格式。
4. “本月”“上个月”等表达应根据当前日期转换。
5. 只说某个月但没有年份时，默认使用当前年份。
6. 用户没有明确指定阈值时，阈值字段必须为null。
7. 无法确认的字段必须为null，不得猜测。
8. 只输出JSON，不要输出Markdown或额外说明。
你还需要判断当前任务是否应该激活可复用Skill。

当前可用Skill：

{available_skill}

Skill选择规则：

1. skill_name和intent是两个不同维度。
2. 普通预算查询不使用Skill。
3. 普通单项风险查询不使用Skill。
4. 单独的制度问答不使用Skill。
5. 只有用户明确要求“全面、综合、系统地审查预算风险”时，
   才选择budget-risk-review。
6. 选择budget-risk-review时，
   intent仍然应该是risk_overview。
7. 不需要Skill时，
   skill_name必须返回null。

示例：

用户：
“研发部2026-07有哪些风险？”
intent = risk_overview
skill_name = null

用户：
“帮我全面审查研发部2026-07的预算风险”
intent = risk_overview
skill_name = budget-risk-review

用户：
“帮我生成研发部2026-07预算报告”
intent = budget_report
skill_name = null
JSON输出格式：

{{
  "intent": "budget_analysis",
  "department_id": "D001",
  "month": "2026-07",
  "growth_threshold": null,
  "large_expense_threshold": null,
  "reason": "用户要求查询指定部门月份的预算执行情况"
}}
""".strip()


def validate_department_id(
    decision: RoutingDecision,
    valid_department_ids: set[str],
) -> RoutingDecision:
    """阻止模型生成不存在的部门编号。"""

    if (
        decision.department_id
        and decision.department_id
        not in valid_department_ids
    ):
        decision.department_id = None

    return decision


def route_user_request(
    user_input: str,
) -> RoutingDecision:
    """调用DeepSeek完成结构化意图识别和参数提取。"""

    cleaned_input = user_input.strip()

    if not cleaned_input:
        raise ValueError("用户输入不能为空")

    departments = get_departments()

    valid_department_ids = (
        get_valid_department_ids(
            departments
        )
    )

    client = get_llm_client()

    response = client.chat.completions.create(
        model=DEFAULT_ROUTER_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    build_router_system_prompt(
                        departments
                    )
                ),
            },
            {
                "role": "user",
                "content": cleaned_input,
            },
        ],
        response_format={
            "type": "json_object",
        },
        temperature=0,
        max_tokens=500,
        stream=False,
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise RuntimeError(
            "路由模型返回了空内容"
        )

    decision = (
        RoutingDecision.model_validate_json(
            content
        )
    )

    return validate_department_id(
        decision=decision,
        valid_department_ids=(
            valid_department_ids
        ),
    )


def run_demo() -> None:
    """测试LLM结构化路由。"""

    test_queries = [
        "帮我看看研发部7月份花得怎么样",
        "研发部上个月有哪些高风险支出？",
        "单笔费用达到50000元需要谁审批？",
        "大额费用按30000元作为阈值，查看D001部门2026-07的风险",
        "今天天气怎么样？",
    ]

    for query in test_queries:
        decision = route_user_request(
            query
        )

        print("\n" + "=" * 70)
        print(f"用户问题：{query}")
        print(
            decision.model_dump_json(
                indent=2,
            )
        )


if __name__ == "__main__":
    run_demo()