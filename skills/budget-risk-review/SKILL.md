---
name: budget-risk-review
description: 对指定部门和月份执行结构化预算风险审查。适用于用户要求全面检查预算执行、超预算、接近预算上限、环比异常增长、大额费用或进一步生成预算报告的场景。
---
# Budget Risk Review

## Purpose

对指定部门和月份执行结构化预算风险审查。

本 Skill 不直接访问数据库，也不重新实现预算规则。
所有业务数据和风险判断必须通过 BudgetPilot 已有 Tool 获取。

## When to Use

当用户表达以下需求时可以使用本 Skill：

- 检查某部门预算执行情况
- 查找预算超支或接近预算上限的项目
- 分析环比异常增长
- 检查大额费用
- 综合判断预算风险
- 在风险分析后生成预算报告

典型请求：

- 帮我全面检查研发部 2026-07 的预算风险
- 看一下 D002 这个月有没有异常支出
- 对研发部做一次预算风险审查

## Required Inputs

必须获得：

- `department_id`
- `month`

其中：

- `department_id` 格式示例：`D002`
- `month` 格式：`YYYY-MM`

如果缺少必要参数，应要求补充或由现有 Agent 参数解析流程获取，
不得自行猜测。

## Available Tools

### budget_analysis_tool

用途：

获取部门各预算类别的预算金额、实际支出、
预算执行率和预算状态。

### risk_overview_tool

用途：

汇总预算风险，包括：

- 接近预算上限
- 超预算
- 环比异常增长
- 大额费用

优先使用该 Tool 获取综合风险结果。

### policy_question_tool

用途：

当需要解释企业预算制度、报销规则或费用政策时，
从企业政策知识库中检索并生成有引用的回答。

仅在风险判断需要制度解释时调用。

### budget_report_tool

用途：

根据预算和风险分析生成正式预算报告。

该操作必须遵守现有 Human-in-the-loop 流程，
在人工批准之前不得执行实际报告生成。

## Workflow

### Step 1: Validate Parameters

确认存在：

- department_id
- month

如果参数无效或缺失，停止执行。

### Step 2: Review Budget Execution

调用：

`budget_analysis_tool`

检查：

- 各预算类别执行率
- 超预算类别
- 接近预算上限类别
- 剩余预算

### Step 3: Review Risk Overview

调用：

`risk_overview_tool`

重点检查：

- 风险总数
- 高风险数量
- 中风险数量
- 超预算风险
- 环比增长异常
- 大额费用异常

### Step 4: Explain Policy When Needed

只有当用户询问：

- 为什么属于风险
- 是否符合公司制度
- 某项费用是否允许
- 报销或预算规则

时调用：

`policy_question_tool`

禁止在没有检索结果的情况下编造制度条款。

### Step 5: Produce Risk Summary

结果应包含：

1. 当前预算执行概况
2. 主要风险
3. 高优先级异常
4. 建议关注项目
5. 如有必要，相关制度依据

风险结论必须基于 Tool 返回的数据，
不得根据语言模型主观猜测。

### Step 6: Generate Report Only When Requested

如果用户明确要求生成预算报告：

调用现有 `budget_report_tool` 流程。

必须经过现有 HITL：

`interrupt -> approval -> resume`

没有人工批准时不得执行报告生成。

## Error Handling

如果 Tool 调用失败：

- 不伪造数据
- 返回当前可确认的信息
- 明确说明失败发生在哪一步

如果 department_id 或 month 缺失：

- 不调用预算分析 Tool
- 不自动猜测具体部门或月份

如果 policy retrieval 没有可靠依据：

- 明确说明当前知识库没有找到足够依据

## Output Principles

输出应：

- 优先呈现高风险问题
- 给出具体类别和指标
- 区分事实数据与建议
- 不夸大风险
- 不暴露数据库内部信息
- 不泄露 API Key、连接字符串或系统内部配置

## Source of Truth

本 Skill 只定义执行流程。

实际业务规则和数据的唯一来源仍然是：

- BudgetPilot Tools
- Service Layer
- Repository Layer
- PostgreSQL
- Policy RAG

如果本 Skill 文档与代码中的业务规则冲突，
以实际业务代码和数据为准。