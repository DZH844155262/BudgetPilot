import type {
  AgentChatResponse,
  BudgetAnalysisDetails,
  BudgetRiskReviewDetails,
  PolicyQuestionDetails,
  PolicySourceDetail,
  RiskAnomaly,
  RiskOverviewDetails,
} from "./api-types";
import type {
  ApprovalTask,
  BudgetCategory,
  BudgetSummaryData,
  MessageCard,
  PolicySource,
  RiskGroup,
  RiskGroupSummary,
  RiskItem,
  RiskOverviewData,
} from "./types";

export interface DetailsMappingResult {
  cards: MessageCard[];
  heading?: string;
  department: string | null;
  month: string | null;
  matched: boolean;
}

const EMPTY_MAPPING: DetailsMappingResult = {
  cards: [],
  department: null,
  month: null,
  matched: false,
};

const ANOMALY_TYPE_LABELS: Record<string, string> = {
  over_budget: "超预算",
  near_budget_limit: "接近上限",
  month_over_month_growth: "环比增长",
  large_expense: "大额费用",
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function toNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

// ---------- type guards ----------

export function isBudgetAnalysisDetails(
  value: unknown,
): value is BudgetAnalysisDetails {
  return (
    isRecord(value) &&
    value.success === true &&
    typeof value.month === "string" &&
    typeof value.department_id === "string" &&
    Array.isArray(value.data)
  );
}

export function isRiskOverviewDetails(
  value: unknown,
): value is RiskOverviewDetails {
  if (!isRecord(value) || value.success !== true || !isRecord(value.data)) {
    return false;
  }
  return isRecord(value.data.summary);
}

export function isBudgetRiskReviewDetails(
  value: unknown,
): value is BudgetRiskReviewDetails {
  return (
    isRecord(value) &&
    value.skill_name === "budget-risk-review" &&
    isRecord(value.budget_analysis) &&
    isRecord(value.risk_overview)
  );
}

export function isPolicyQuestionDetails(
  value: unknown,
): value is PolicyQuestionDetails {
  if (!isRecord(value) || value.success !== true || !isRecord(value.data)) {
    return false;
  }
  return (
    typeof value.data.answer === "string" &&
    Array.isArray(value.data.sources)
  );
}

// ---------- mappers ----------

function mapBudgetAnalysisToCard(
  details: BudgetAnalysisDetails,
): MessageCard {
  const items = details.data;
  const annualBudget = items.reduce(
    (sum, item) => sum + toNumber(item.budget_amount),
    0,
  );
  const spent = items.reduce(
    (sum, item) => sum + toNumber(item.actual_amount),
    0,
  );
  const categories: BudgetCategory[] = items.map((item) => ({
    name: item.category,
    budget: toNumber(item.budget_amount),
    spent: toNumber(item.actual_amount),
    riskStatus: item.risk_status,
  }));

  const data: BudgetSummaryData = {
    department: details.department_id,
    period: details.month,
    annualBudget,
    spent,
    commitment: 0,
    categories,
  };

  return { kind: "budget-summary", data };
}

function mapAnomalyToRiskItem(
  anomaly: RiskAnomaly,
  group: RiskGroup,
  index: number,
): RiskItem {
  const typeLabel =
    ANOMALY_TYPE_LABELS[anomaly.anomaly_type] ?? anomaly.anomaly_type;
  return {
    id: `${group}-${index}`,
    severity: anomaly.severity,
    title: `${anomaly.category} · ${typeLabel}`,
    description: anomaly.message,
    status: typeLabel,
    group,
  };
}

function mapRiskOverviewToCard(
  details: RiskOverviewDetails,
): MessageCard {
  const data = details.data;
  const summary = data.summary;

  const budgetRisks = (data.budget_anomalies ?? []).map((anomaly, index) =>
    mapAnomalyToRiskItem(anomaly, "budget", index),
  );
  const growthRisks = (data.growth_anomalies ?? []).map((anomaly, index) =>
    mapAnomalyToRiskItem(anomaly, "growth", index),
  );
  const largeExpenseRisks = (data.large_expense_anomalies ?? []).map(
    (anomaly, index) =>
      mapAnomalyToRiskItem(anomaly, "large_expense", index),
  );

  const totalCount = summary.total_anomaly_count;
  const highCount = summary.high_risk_count;
  const mediumCount = summary.medium_risk_count;

  const groups: RiskGroupSummary[] = [
    { key: "budget", label: "预算异常", count: budgetRisks.length },
    { key: "growth", label: "环比异常", count: growthRisks.length },
    { key: "large_expense", label: "大额费用", count: largeExpenseRisks.length },
  ];

  const cardData: RiskOverviewData = {
    department: data.department_id ?? details.department_id,
    period: data.month ?? details.month,
    riskCount: totalCount,
    highCount,
    mediumCount,
    lowCount: Math.max(totalCount - highCount - mediumCount, 0),
    risks: [...budgetRisks, ...growthRisks, ...largeExpenseRisks],
    groups,
  };

  return { kind: "risk-overview", data: cardData };
}

function mapSkillToCards(details: BudgetRiskReviewDetails): MessageCard[] {
  const cards: MessageCard[] = [];
  if (isBudgetAnalysisDetails(details.budget_analysis)) {
    cards.push(mapBudgetAnalysisToCard(details.budget_analysis));
  }
  if (isRiskOverviewDetails(details.risk_overview)) {
    cards.push(mapRiskOverviewToCard(details.risk_overview));
  }
  return cards;
}

function mapPolicySources(sources: PolicySourceDetail[]): PolicySource[] {
  return sources.map((source, index) => ({
    id: source.chunk_id || `source-${index}`,
    title: source.document_title || source.source || "未命名制度",
    section: source.section_title || undefined,
    path: source.source || undefined,
    similarity:
      typeof source.similarity_score === "number"
        ? source.similarity_score
        : undefined,
  }));
}

/** 将后端 approval_request 转换为前端审批任务；非审批响应返回 null */
export function buildApprovalTask(
  response: AgentChatResponse,
): ApprovalTask | null {
  if (!response.requires_approval || !isRecord(response.approval_request)) {
    return null;
  }
  const request = response.approval_request;
  return {
    id: response.thread_id,
    action: typeof request.action === "string" ? request.action : "unknown",
    department:
      typeof request.department_id === "string"
        ? request.department_id
        : response.department_id ?? "—",
    month:
      typeof request.month === "string"
        ? request.month
        : response.month ?? "—",
    message:
      typeof request.message === "string"
        ? request.message
        : "当前操作需要人工确认。",
    status: "pending",
    threadId: response.thread_id,
  };
}

// ---------- 入口 ----------

export function mapDetailsToCards(
  response: AgentChatResponse,
): DetailsMappingResult {
  const details = response.details;
  const topLevelDepartment = response.department_id ?? null;
  const topLevelMonth = response.month ?? null;

  if (!isRecord(details)) {
    return {
      ...EMPTY_MAPPING,
      department: topLevelDepartment,
      month: topLevelMonth,
    };
  }

  // Skill：综合预算风险审查（同一消息内展示预算 + 风险两张卡片）
  if (
    response.intent === "risk_overview" &&
    details.skill_name === "budget-risk-review" &&
    isBudgetRiskReviewDetails(details)
  ) {
    const cards = mapSkillToCards(details);
    return {
      cards,
      heading: "综合预算风险审查",
      department:
        details.budget_analysis.department_id ?? topLevelDepartment,
      month: details.budget_analysis.month ?? topLevelMonth,
      matched: cards.length > 0,
    };
  }

  if (response.intent === "budget_analysis" && isBudgetAnalysisDetails(details)) {
    return {
      cards: [mapBudgetAnalysisToCard(details)],
      department: details.department_id,
      month: details.month,
      matched: true,
    };
  }

  if (response.intent === "risk_overview" && isRiskOverviewDetails(details)) {
    const card = mapRiskOverviewToCard(details);
    return {
      cards: [card],
      department: details.data.department_id ?? details.department_id,
      month: details.data.month ?? details.month,
      matched: true,
    };
  }

  if (response.intent === "policy_question" && isPolicyQuestionDetails(details)) {
    const sources = mapPolicySources(details.data.sources);
    return {
      cards:
        sources.length > 0 ? [{ kind: "policy-source", data: sources }] : [],
      heading:
        sources.length > 0 ? `参考制度依据 ${sources.length} 条` : undefined,
      department: topLevelDepartment,
      month: topLevelMonth,
      matched: true,
    };
  }

  return {
    ...EMPTY_MAPPING,
    department: topLevelDepartment,
    month: topLevelMonth,
  };
}

function describeTarget(
  department: string | null,
  month: string | null,
): string {
  const parts: string[] = [];
  if (department) parts.push(`${department} 部门`);
  if (month) parts.push(month);
  return parts.join(" ");
}

/** 提取预算报告的管理层关注摘要（清晰的文本，避免渲染整段 JSON） */
function extractReportManagementSummary(
  details: Record<string, unknown>,
): string {
  if (!isRecord(details.data)) {
    return "";
  }
  const summary = details.data.management_summary;
  return typeof summary === "string" && summary.trim() ? summary.trim() : "";
}

/** 用简短标题替代包含序列化 JSON 的 answer */
export function buildDisplayAnswer(
  response: AgentChatResponse,
  mapping: DetailsMappingResult,
): string {
  // 预算报告已生成：details.success === true 表示批准后工具执行成功，
  // 用简短标题替代 answer 中的整段序列化 JSON；
  // 拒绝（details={}）或生成失败（success=false）时保留原始 answer。
  if (
    response.intent === "budget_report" &&
    response.status === "completed" &&
    isRecord(response.details) &&
    response.details.success === true
  ) {
    const target = describeTarget(
      mapping.department ?? response.department_id,
      mapping.month ?? response.month,
    );
    const title = target
      ? `已生成 ${target} 的预算报告。`
      : "预算报告已生成。";
    const managementSummary = extractReportManagementSummary(response.details);
    return managementSummary ? `${title}\n\n${managementSummary}` : title;
  }

  if (!mapping.matched) {
    return response.answer;
  }

  const target = describeTarget(mapping.department, mapping.month);

  if (mapping.heading === "综合预算风险审查") {
    return target
      ? `已完成 ${target} 的综合预算风险审查。`
      : "已完成综合预算风险审查。";
  }

  if (response.intent === "budget_analysis") {
    return target
      ? `已完成 ${target} 的预算执行分析。`
      : "已完成预算执行分析。";
  }

  if (response.intent === "risk_overview") {
    return target
      ? `已完成 ${target} 的风险分析。`
      : "已完成风险分析。";
  }

  return response.answer;
}
