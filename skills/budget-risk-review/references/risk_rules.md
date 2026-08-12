# BudgetPilot Risk Rules Reference

本文件用于帮助理解 Budget Risk Review Skill。

注意：
实际判断逻辑以 BudgetPilot Service 和 Tool 返回结果为准，
本文件不是业务逻辑执行代码。

## Budget Execution

当前项目基础预算执行规则：

- 执行率 > 100%：超预算
- 执行率 90% - 100%：接近预算上限
- 执行率 < 90%：正常范围

## Month-over-Month Growth

默认异常增长阈值：

20%

实际执行时应使用 `risk_overview_tool`
或底层 Service 当前配置的阈值。

## Large Expense

当前默认大额费用阈值：

20000

实际执行时仍以 Tool / Service 参数为准。

## Risk Review Principle

风险审查应综合考虑：

- 预算执行率
- 超预算
- 接近预算上限
- 环比增长异常
- 大额费用

不要根据单一指标直接推断整个部门存在严重财务风险。

## Human Approval

预算报告生成采用 Human-in-the-loop。

流程：

用户提出报告请求

→ Agent 准备执行

→ LangGraph interrupt

→ Checkpoint 持久化

→ 用户批准或拒绝

→ Command(resume)

→ 批准后执行 budget_report_tool