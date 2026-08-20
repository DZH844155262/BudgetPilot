# 企业预算费用分析助手（Enterprise Budget Analysis Agent）

> 基于 **LangGraph + RAG + FastAPI + PostgreSQL + Next.js** 构建的企业级
> AI Agent
> 应用，实现自然语言驱动的预算分析、风险检测、制度问答和报告生成。

## 项目简介

传统企业预算管理系统通常依赖复杂菜单和固定操作流程，业务人员需要学习大量系统操作。

本项目通过 AI Agent 将用户自然语言需求转换为可执行任务：

    用户输入需求
            ↓
    Agent理解用户意图
            ↓
    LangGraph工作流编排
            ↓
    Tool调用业务能力
            ↓
    数据库查询 / RAG检索
            ↓
    结果生成

用户无需手动寻找功能入口，只需要描述目标即可完成预算分析任务。

------------------------------------------------------------------------

# Demo 展示

## 1. 自然语言预算查询

用户输入：

    帮我看看研发部2026年7月预算情况

Agent 自动完成：

-   意图识别
-   参数提取（部门、月份）
-   调用预算分析 Tool
-   查询 PostgreSQL业务数据
-   返回结构化分析结果

```{=html}
<!-- 请替换为你的第一张截图 -->
```
`<img src="./docs/images/budget_analysis.png" width="850">`{=html}

------------------------------------------------------------------------

## 2. 多轮对话风险分析

基于 LangGraph State 和 PostgresSaver 实现会话上下文保存。

用户继续输入：

    那风险呢？

Agent 自动继承上一轮上下文：

    department = 研发部
    month = 2026-07

并调用风险分析 Tool。

```{=html}
<!-- 请替换为你的第二张截图 -->
```
`<img src="./docs/images/risk_analysis.png" width="850">`{=html}

------------------------------------------------------------------------

## 3. Human-in-the-Loop 报告生成

对于需要确认的操作，Agent不会直接执行。

用户输入：

    帮我生成研发部2026年7月预算报告

执行流程：

    预算报告请求
            ↓
    LangGraph interrupt暂停
            ↓
    等待用户确认
            ↓
    Command(resume)
            ↓
    继续执行报告生成 Tool

```{=html}
<!-- 请替换为你的第三张截图 -->
```
`<img src="./docs/images/hitl_report.png" width="850">`{=html}

------------------------------------------------------------------------

# 核心功能

## 1. Agent Workflow

使用 LangGraph 构建可控 Agent 工作流：

-   Structured Router 意图识别
-   State状态管理
-   Tool Calling
-   Checkpoint持久化
-   Human-in-the-Loop审批
-   Agent Skill加载

支持任务：

    budget_analysis
    risk_overview
    policy_question
    budget_report

------------------------------------------------------------------------

# 2. Tool Calling 与业务系统集成

项目没有让大语言模型直接访问数据库。

采用分层架构：

    Agent
     ↓
    Tool
     ↓
    Service
     ↓
    Repository
     ↓
    PostgreSQL

职责划分：

### Agent

负责：

-   理解用户需求
-   选择执行路径
-   调度工具

### Tool

提供受控业务能力：

-   预算查询
-   风险分析
-   报告生成

### Service

负责：

-   预算计算
-   风险规则
-   数据处理

### Repository

负责：

-   数据访问
-   SQL查询

这种设计避免：

    LLM
     ↓
    直接生成SQL
     ↓
    访问数据库

提高系统稳定性和可维护性。

------------------------------------------------------------------------

# 3. RAG 企业制度问答

针对企业内部制度文档构建 RAG Pipeline。

流程：

    企业制度文档
            ↓
    文本切分
            ↓
    BGE Embedding
            ↓
    pgvector向量检索
            ↓
    BGE Reranker精排
            ↓
    DeepSeek生成答案

支持：

-   企业制度查询
-   来源引用
-   降低模型幻觉

```{=html}
<!-- 可选截图：RAG问答 -->
```
`<img src="./docs/images/rag_answer.png" width="850">`{=html}

------------------------------------------------------------------------

# 4. Memory 多轮会话

使用 LangGraph Checkpoint 机制保存 Agent 状态。

保存：

-   用户上下文
-   部门参数
-   月份信息
-   查询结果

例如：

第一轮：

    查询研发部7月预算

第二轮：

    那风险呢？

系统可以自动恢复上下文。

------------------------------------------------------------------------

# 系统架构

```{=html}
<!-- 请替换为架构图 -->
```
`<img src="./docs/images/architecture.png" width="900">`{=html}

整体：

    Next.js
        ↓
    FastAPI
        ↓
    LangGraph Agent
        ↓
    Router
        ↓
    Tools
        ↓
    Business Service
        ↓
    PostgreSQL


    RAG:

    Document
        ↓
    Embedding
        ↓
    pgvector
        ↓
    Reranker
        ↓
    LLM

------------------------------------------------------------------------

# 技术栈

## Agent / LLM

-   LangGraph
-   DeepSeek API
-   Tool Calling
-   Structured Output
-   Human-in-the-Loop

## RAG

-   BGE Embedding
-   pgvector
-   BGE Reranker
-   DeepEval

## Backend

-   Python
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic

## Frontend

-   Next.js
-   React
-   TypeScript

## Engineering

-   pytest
-   GitHub Actions
-   Docker

------------------------------------------------------------------------

# 项目结构

    BudgetPilot/

    ├── agent/
    ├── tools/
    ├── services/
    ├── repository/
    ├── rag/
    ├── frontend/
    ├── tests/
    ├── evaluation/
    └── README.md

------------------------------------------------------------------------

# RAG Evaluation

采用冻结测试集进行检索与生成评估：

Retrieval:

-   Recall@3
-   MRR
-   nDCG

Generation:

-   Faithfulness
-   Answer Relevancy
-   Citation

```{=html}
<!-- 可放评测截图 -->
```
`<img src="./docs/images/evaluation.png" width="850">`{=html}

------------------------------------------------------------------------

# Engineering Highlights

## 为什么使用 LangGraph？

相比传统 if-else 工作流：

LangGraph提供：

-   显式状态管理
-   条件路由
-   Checkpoint恢复
-   人工审批
-   可扩展工作流

## 为什么 Tool 不直接让 LLM 操作数据库？

因为预算系统需要保证：

-   数据准确性
-   业务规则稳定
-   可测试性

LLM负责理解和生成，确定性逻辑交给代码执行。

------------------------------------------------------------------------

# Future Work

-   Hybrid Retrieval
-   权限控制
-   Agent Observability
-   Docker部署
-   更多企业 Agent Skill

------------------------------------------------------------------------

# Disclaimer

本项目使用模拟企业预算、费用和制度数据，仅用于 Agent
工程实践和作品集展示。
