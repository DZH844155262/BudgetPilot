from app.agent.router_service import (
    route_user_request,
)
from app.agent.skill_registry import (
    load_skill,
)
from langgraph.graph import END, START, StateGraph
from app.agent.checkpointer import (
    checkpointer,
)
from langgraph.types import interrupt
from app.agent.state import AgentIntent, AgentState

import json
import re

from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentIntent, AgentState
from app.agent.tools import (
    budget_analysis_tool,
    budget_report_tool,
    policy_question_tool,
    risk_overview_tool,
)
from app.agent.router_service import (
    route_user_request,
)
from app.budget_service import (
    get_departments,
)
def add_trace(
    state: AgentState,
    step: str,
) -> list[str]:
    """在不修改原列表的情况下追加执行轨迹。"""

    return [
        *state.get("trace", []),
        step,
    ]


def normalize_input_node(
    state: AgentState,
) -> dict:
    """清理当前轮用户输入，并重置当前轮临时状态。"""

    user_input = state.get(
        "user_input",
        "",
    ).strip()

    if not user_input:
        return {
            "intent": "unknown",
            "error": "用户输入不能为空",
            "response": "",
            "tool_result": {},
            "trace": [
                "normalize_input"
            ],
        }

    return {
        "user_input": user_input,

        # 当前轮重新计算
        "intent": "unknown",
        "error": "",
        "response": "",
        "tool_result": {},
        "routing_source": "",
        "route_reason": "",
        "skill_name": None,
        "skill_content": None,
        # 每一轮重新记录执行轨迹
        "trace": [
            "normalize_input"
        ],

        # 注意：
        # 不重置department_id和month，
        # 因为这两个属于会话上下文。
    }

def classify_intent_node(
    state: AgentState,
) -> dict:
    """使用DeepSeek结构化识别意图和参数。

    LLM调用失败时自动退回关键词路由，
    避免整个Agent不可用。
    """

    if state.get("error"):
        return {
            "intent": "unknown",
            "routing_source": "input_error",
            "route_reason": (
                "输入校验失败"
            ),
            "skill_name": None,
            "skill_content": None,
            "trace": add_trace(
                state,
                "classify_intent",
            ),
        }

    user_input = state["user_input"]

    try:
        decision = route_user_request(
            user_input
        )

        # Router只返回Skill名称。
        # 只有真正选中Skill时，
        # 才加载完整SKILL.md。
        skill_name = getattr(
            decision,
            "skill_name",
            None,
        )

        skill_content = None

        if skill_name:
            skill_content = load_skill(
                skill_name
            )

        updates: dict = {
            "intent": decision.intent,
            "routing_source": "llm",
            "route_reason": (
                decision.reason
            ),
            "skill_name": skill_name,
            "skill_content": skill_content,
            "trace": add_trace(
                state,
                "classify_intent",
            ),
        }

        if decision.department_id:
            updates["department_id"] = (
                decision.department_id
            )

        if decision.month:
            updates["month"] = (
                decision.month
            )

        if (
            decision.growth_threshold
            is not None
        ):
            updates["growth_threshold"] = (
                decision.growth_threshold
            )

        if (
            decision.large_expense_threshold
            is not None
        ):
            updates[
                "large_expense_threshold"
            ] = (
                decision
                .large_expense_threshold
            )

        return updates

    except Exception as exc:
        fallback_intent = (
            classify_intent_by_keywords(
                user_input
            )
        )

        return {
            "intent": fallback_intent,
            "routing_source": (
                "keyword_fallback"
            ),
            "route_reason": (
                "LLM路由不可用，"
                f"已使用关键词兜底："
                f"{type(exc).__name__}"
            ),
            "skill_name": None,
            "skill_content": None,
            "trace": add_trace(
                state,
                "classify_intent",
            ),
        }



        if decision.department_id:
            updates["department_id"] = (
                decision.department_id
            )

        if decision.month:
            updates["month"] = (
                decision.month
            )

        if (
            decision.growth_threshold
            is not None
        ):
            updates["growth_threshold"] = (
                decision.growth_threshold
            )

        if (
            decision.large_expense_threshold
            is not None
        ):
            updates[
                "large_expense_threshold"
            ] = (
                decision
                .large_expense_threshold
            )

        return updates

    except Exception as exc:
        fallback_intent = (
            classify_intent_by_keywords(
                user_input
            )
        )

        return {
            "intent": fallback_intent,
            "routing_source": (
                "keyword_fallback"
            ),
            "route_reason": (
                "LLM路由不可用，"
                f"已使用关键词兜底："
                f"{type(exc).__name__}"
            ),
            "trace": add_trace(
                state,
                "classify_intent",
            ),
        }
def extract_analysis_parameters_node(
    state: AgentState,
) -> dict:
    """提取预算分析和风险分析所需的通用参数。"""

    user_input = state.get(
        "user_input",
        "",
    )

    month = state.get("month")
    department_id = state.get(
        "department_id"
    )

    if not month:
        month_match = re.search(
    r"(?<!\d)\d{4}-(?:0[1-9]|1[0-2])(?!\d)",
    user_input,
)

        if month_match:
            month = month_match.group(0)

    if not department_id:
        department_match = re.search(
    r"(?<![A-Z0-9])D\d{3}(?![A-Z0-9])",
    user_input.upper(),
)

        if department_match:
            department_id = (
                department_match.group(0)
            )
    # 如果LLM和部门编号正则都没有提取到部门，
    # 再使用真实部门表按中文名称做确定性匹配。
    if not department_id:
        departments = get_departments()

        for department in departments:
            department_name = str(
                department.get(
                    "department_name",
                    "",
                )
            ).strip()

            candidate_id = str(
                department.get(
                    "department_id",
                    "",
                )
            ).strip()

            if (
                department_name
                and candidate_id
                and department_name
                in user_input
            ):
                department_id = candidate_id
                break
    updates: dict = {
        "trace": add_trace(
            state,
            "extract_analysis_parameters",
        ),
    }

    if month:
        updates["month"] = month

    if department_id:
        updates["department_id"] = (
            department_id
        )

    missing_parameters = []

    if not department_id:
        missing_parameters.append("部门编号")

    if not month:
        missing_parameters.append("查询月份")

    if missing_parameters:
        updates["error"] = (
    "查询缺少必要参数："
    + "、".join(missing_parameters)
    + "。请输入类似："
    + "分析D001部门2026-07的预算情况。"
)

    return updates

def budget_analysis_node(
    state: AgentState,
) -> dict:
    """调用真实预算分析工具。"""

    if state.get("error"):
        return {
            "response": state["error"],
            "trace": add_trace(
                state,
                "extract_analysis_parameters",
            ),
        }

    month = state.get("month")
    department_id = state.get(
        "department_id"
    )

    if not month or not department_id:
        error_message = (
            "预算分析参数不完整，"
            "无法调用预算分析工具。"
        )

        return {
            "error": error_message,
            "response": error_message,
            "trace": add_trace(
                state,
                "budget_analysis",
            ),
        }

    try:
        tool_result = (
            budget_analysis_tool.invoke(
                {
                    "month": month,
                    "department_id": (
                        department_id
                    ),
                }
            )
        )

    except Exception as exc:
        error_message = (
            "预算分析工具执行失败："
            f"{exc}"
        )

        return {
            "error": error_message,
            "response": (
                "预算分析暂时执行失败，"
                "请检查数据库连接和查询参数。"
            ),
            "trace": add_trace(
                state,
                "budget_analysis",
            ),
        }

    if not tool_result["success"]:
        return {
            "tool_result": tool_result,
            "error": tool_result["error"],
            "response": (
                "预算分析失败："
                f"{tool_result['error']}"
            ),
            "trace": add_trace(
                state,
                "budget_analysis",
            ),
        }

    formatted_data = json.dumps(
        tool_result["data"],
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return {
        "tool_result": tool_result,
        "response": (
            f"已完成{department_id}部门"
            f"{month}的预算分析，"
            f"共返回"
            f"{tool_result['result_count']}条结果："
            f"\n{formatted_data}"
        ),
        "trace": add_trace(
            state,
            "budget_analysis",
        ),
    }


def risk_overview_node(
    state: AgentState,
) -> dict:
    """执行风险分析。

    普通风险查询只调用risk_overview_tool。
    激活budget-risk-review Skill时，
    会同时执行预算执行分析和综合风险分析。
    """

    if state.get("error"):
        return {
            "response": state["error"],
            "trace": add_trace(
                state,
                "risk_overview",
            ),
        }

    month = state.get("month")
    department_id = state.get(
        "department_id"
    )

    if not month or not department_id:
        error_message = (
            "风险分析参数不完整，"
            "无法调用风险概览工具。"
        )

        return {
            "error": error_message,
            "response": error_message,
            "trace": add_trace(
                state,
                "risk_overview",
            ),
        }

    growth_threshold = float(
        state.get(
            "growth_threshold",
            20.0,
        )
    )

    large_expense_threshold = float(
        state.get(
            "large_expense_threshold",
            20000.0,
        )
    )

    skill_name = state.get(
        "skill_name"
    )

    # =====================================
    # 1. 如果激活Skill，先做预算执行分析
    # =====================================

    budget_result = None

    if skill_name == "budget-risk-review":
        try:
            budget_result = (
                budget_analysis_tool.invoke(
                    {
                        "month": month,
                        "department_id": (
                            department_id
                        ),
                    }
                )
            )

        except Exception as exc:
            error_message = (
                "预算风险审查中的预算分析失败："
                f"{exc}"
            )

            return {
                "error": error_message,
                "response": (
                    "预算风险审查暂时执行失败，"
                    "预算执行分析步骤未完成。"
                ),
                "trace": add_trace(
                    state,
                    "budget-risk-review",
                ),
            }

        if not budget_result["success"]:
            return {
                "tool_result": budget_result,
                "error": budget_result["error"],
                "response": (
                    "预算风险审查失败："
                    f"{budget_result['error']}"
                ),
                "trace": add_trace(
                    state,
                    "budget-risk-review",
                ),
            }

    # =====================================
    # 2. 所有风险请求都执行综合风险分析
    # =====================================

    try:
        risk_result = (
            risk_overview_tool.invoke(
                {
                    "month": month,
                    "department_id": (
                        department_id
                    ),
                    "growth_threshold": (
                        growth_threshold
                    ),
                    "large_expense_threshold": (
                        large_expense_threshold
                    ),
                }
            )
        )

    except Exception as exc:
        error_message = (
            "风险概览工具执行失败："
            f"{exc}"
        )

        return {
            "error": error_message,
            "response": (
                "风险分析暂时执行失败，"
                "请检查数据库连接和查询参数。"
            ),
            "trace": add_trace(
                state,
                "risk_overview",
            ),
        }

    if not risk_result["success"]:
        return {
            "tool_result": risk_result,
            "error": risk_result["error"],
            "response": (
                "风险分析失败："
                f"{risk_result['error']}"
            ),
            "trace": add_trace(
                state,
                "risk_overview",
            ),
        }

    # =====================================
    # 3. Skill模式：合并两个Tool的结果
    # =====================================

    if skill_name == "budget-risk-review":
        combined_result = {
            "skill_name": skill_name,
            "budget_analysis": (
                budget_result
            ),
            "risk_overview": (
                risk_result
            ),
        }

        formatted_data = json.dumps(
            combined_result,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        return {
            "growth_threshold": (
                growth_threshold
            ),
            "large_expense_threshold": (
                large_expense_threshold
            ),
            "tool_result": combined_result,
            "response": (
                f"已按照{skill_name} Skill完成"
                f"{department_id}部门"
                f"{month}的综合预算风险审查。"
                f"\n审查包含："
                f"\n1. 预算执行情况"
                f"\n2. 综合风险概览"
                f"\n结果："
                f"\n{formatted_data}"
            ),
            "trace": [
                *add_trace(
                    state,
                    "risk_overview",
                ),
                "skill:budget-risk-review",
            ],
        }

    # =====================================
    # 4. 普通风险查询保持原逻辑
    # =====================================

    formatted_data = json.dumps(
        risk_result["data"],
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return {
        "growth_threshold": (
            growth_threshold
        ),
        "large_expense_threshold": (
            large_expense_threshold
        ),
        "tool_result": risk_result,
        "response": (
            f"已完成{department_id}部门"
            f"{month}的风险分析。"
            f"\n环比增长阈值："
            f"{growth_threshold}%"
            f"\n大额费用阈值："
            f"{large_expense_threshold}元"
            f"\n风险结果："
            f"\n{formatted_data}"
        ),
        "trace": add_trace(
            state,
            "risk_overview",
        ),
    }




def policy_question_node(
    state: AgentState,
) -> dict:
    """调用真实企业制度问答工具。"""

    user_input = state.get(
        "user_input",
        "",
    ).strip()

    if not user_input:
        error_message = (
            "制度问题不能为空。"
        )

        return {
            "error": error_message,
            "response": error_message,
            "trace": add_trace(
                state,
                "policy_question",
            ),
        }

    try:
        tool_result = (
            policy_question_tool.invoke(
                {
                    "query": user_input,
                    "top_k": 2,
                }
            )
        )

    except Exception as exc:
        error_message = (
            "制度问答工具执行失败："
            f"{exc}"
        )

        return {
            "error": error_message,
            "response": (
                "制度问答暂时执行失败，"
                "请检查模型、数据库和向量检索服务。"
            ),
            "trace": add_trace(
                state,
                "policy_question",
            ),
        }

    if not tool_result["success"]:
        return {
            "tool_result": tool_result,
            "error": tool_result["error"],
            "response": (
                "制度问答失败："
                f"{tool_result['error']}"
            ),
            "trace": add_trace(
                state,
                "policy_question",
            ),
        }

    result_data = tool_result["data"]

    answer = result_data.get(
        "answer",
        "未生成制度回答。",
    )

    sources = result_data.get(
        "sources",
        [],
    )

    return {
        "tool_result": tool_result,
        "response": answer,
        "trace": add_trace(
            state,
            "policy_question",
        ),
    }
def budget_report_node(
    state: AgentState,
) -> dict:
    """生成预算报告，并在真正执行前要求人工确认。"""

    if state.get("error"):
        return {
            "response": state["error"],
            "trace": add_trace(
                state,
                "budget_report",
            ),
        }

    month = state.get("month")
    department_id = state.get(
        "department_id"
    )

    if not month or not department_id:
        error_message = (
            "生成预算报告缺少必要参数。"
        )

        return {
            "error": error_message,
            "response": error_message,
            "trace": add_trace(
                state,
                "budget_report",
            ),
        }

    # Human-in-the-loop：
    # 程序执行到这里暂停，等待人工确认
    approved = interrupt(
        {
            "type": "budget_report_approval",
            "action": "generate_budget_report",
            "department_id": department_id,
            "month": month,
            "message": (
                f"即将生成{department_id}部门"
                f"{month}的预算分析报告，"
                "是否继续？"
            ),
        }
    )

    # 用户拒绝
    if approved is not True:
        return {
            "approval_status": "rejected",
            "response": (
                f"已取消生成{department_id}部门"
                f"{month}的预算报告。"
            ),
            "trace": add_trace(
                state,
                "budget_report",
            ),
        }

    # 用户批准之后，才真正调用Tool
    tool_result = budget_report_tool.invoke(
        {
            "month": month,
            "department_id": department_id,
        }
    )

    if not tool_result["success"]:
        return {
            "approval_status": "approved",
            "tool_result": tool_result,
            "error": tool_result["error"],
            "response": (
                "预算报告生成失败："
                f"{tool_result['error']}"
            ),
            "trace": add_trace(
                state,
                "budget_report",
            ),
        }

    formatted_report = json.dumps(
        tool_result["data"],
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return {
        "approval_status": "approved",
        "tool_result": tool_result,
        "response": (
            f"已生成{department_id}部门"
            f"{month}的预算报告："
            f"\n{formatted_report}"
        ),
        "trace": add_trace(
            state,
            "budget_report",
        ),
    }

def fallback_node(
    state: AgentState,
) -> dict:
    """无法识别任务时的兜底节点。"""

    error = state.get("error")

    if error:
        response = error
    else:
        response = (
            "暂时无法判断你的需求。"
            "目前支持预算分析、风险分析"
            "和企业制度问答。"
        )

    return {
        "response": response,
        "trace": add_trace(
            state,
            "fallback",
        ),
    }


def select_route(
    state: AgentState,
) -> AgentIntent:
    """根据意图选择下一个节点。"""

    return state.get(
        "intent",
        "unknown",
    )


def build_budget_agent_graph():
    """构建并编译BudgetPilot最小工作流。"""

    builder = StateGraph(AgentState)
    builder.add_node(
        "budget_report",
        budget_report_node,
    )
    builder.add_node(
        "normalize_input",
        normalize_input_node,
    )

    builder.add_node(
        "classify_intent",
        classify_intent_node,
    )

    builder.add_node(
        "budget_analysis",
        budget_analysis_node,
    )

    builder.add_node(
        "risk_overview",
        risk_overview_node,
    )

    builder.add_node(
        "policy_question",
        policy_question_node,
    )

    builder.add_node(
        "fallback",
        fallback_node,
    )
    builder.add_node(
    "extract_analysis_parameters",
    extract_analysis_parameters_node,
)

    builder.add_edge(
        START,
        "normalize_input",
    )

    builder.add_edge(
        "normalize_input",
        "classify_intent",
    )
    builder.add_conditional_edges(
    "extract_analysis_parameters",
    select_route,
    {
        "budget_analysis": (
            "budget_analysis"
        ),
        "risk_overview": (
            "risk_overview"
        ),
        "budget_report": (
            "budget_report"
        ),
        "policy_question": (
            "policy_question"
        ),
        "unknown": "fallback",
    },
)

    builder.add_conditional_edges(
    "classify_intent",
    select_route,
    {
        "budget_analysis": (
            "extract_analysis_parameters"
        ),
        "risk_overview": (
            "extract_analysis_parameters"
        ),
        "budget_report": (
            "extract_analysis_parameters"
        ),
        "policy_question": (
            "policy_question"
        ),
        "unknown": "fallback",
    },
)

    builder.add_edge(
        "budget_analysis",
        END,
    )

    
    builder.add_edge(
        "risk_overview",
        END,
    )

    builder.add_edge(
        "policy_question",
        END,
    )

    builder.add_edge(
        "fallback",
        END,
    )
    builder.add_edge(
        "budget_report",
         END,
)
    return builder.compile(
    checkpointer=checkpointer
)


budget_agent_graph = (
    build_budget_agent_graph()
)


def run_demo() -> None:
    """运行四个路由演示用例。"""

    test_queries = [
    "帮我分析D001部门2026-07的预算执行情况",
    "D001部门2026-07有哪些高风险异常？",
    "单笔费用达到50000元需要谁审批？",
    "今天天气怎么样？",
]

    for query in test_queries:
        result = budget_agent_graph.invoke(
            {
                "user_input": query,
                "trace": [],
            }
        )

        print("\n" + "=" * 70)
        print(f"用户问题：{query}")
        print(
            f"识别意图："
            f"{result.get('intent')}"
        )
        print(
            f"最终回答："
            f"{result.get('response')}"
        )
        print(
            f"执行轨迹："
            f"{result.get('trace')}"
        )


if __name__ == "__main__":
    run_demo()



def classify_intent_by_keywords(
    user_input: str,
) -> AgentIntent:
    """当LLM路由失败时使用的确定性兜底规则。"""
    report_keywords = [
        "生成报告",
        "预算报告",
        "风险报告",
        "分析报告",
        "制作报告",
        "输出报告",
    ]
    policy_keywords = [
        "制度",
        "报销",
        "审批",
        "复核",
        "材料",
        "规定",
    ]

    risk_keywords = [
        "风险",
        "异常",
        "预警",
        "重点关注",
    ]

    budget_keywords = [
        "预算",
        "执行率",
        "支出",
        "费用情况",
        "花得怎么样",
    ]
    if any(
        keyword in user_input
        for keyword in report_keywords
    ):
        return "budget_report"
    if any(
        keyword in user_input
        for keyword in policy_keywords
    ):
        return "policy_question"

    if any(
        keyword in user_input
        for keyword in risk_keywords
    ):
        return "risk_overview"

    if any(
        keyword in user_input
        for keyword in budget_keywords
    ):
        return "budget_analysis"

    return "unknown"