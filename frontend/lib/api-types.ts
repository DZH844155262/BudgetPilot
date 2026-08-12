export type AgentIntent =
  | "budget_analysis"
  | "risk_overview"
  | "policy_question"
  | "budget_report"
  | "unknown";

export type AgentStatus =
  | "completed"
  | "waiting_for_approval";

export interface AgentApprovalRequest {
  type?: string;
  action?: string;
  department_id?: string;
  month?: string;
  message?: string;
  [key: string]: unknown;
}

export type AgentDetails =
  Record<string, unknown>;

/** 预算执行分析：单条费用科目明细 */
export interface BudgetAnalysisItem {
  month: string;
  department_id: string;
  category: string;
  budget_amount: number;
  actual_amount: number;
  execution_rate: number;
  variance: number;
  remaining: number;
  risk_status: "正常" | "预警" | "超预算";
}

/** budget_analysis 意图的 details */
export interface BudgetAnalysisDetails {
  success: boolean;
  month: string;
  department_id: string;
  result_count: number;
  data: BudgetAnalysisItem[];
}

export type RiskAnomalySeverity = "high" | "medium" | "low";

export type RiskAnomalyType =
  | "over_budget"
  | "near_budget_limit"
  | "month_over_month_growth"
  | "large_expense";

/** 风险/异常条目（预算异常、环比异常、大额费用通用） */
export interface RiskAnomaly {
  anomaly_type: RiskAnomalyType;
  severity: RiskAnomalySeverity;
  category: string;
  message: string;
  execution_rate?: number;
  amount?: number;
  current_amount?: number;
  previous_amount?: number;
  growth_rate?: number;
  expense_id?: string;
  date?: string;
  threshold?: number;
  description?: string;
}

export interface RiskSummary {
  total_anomaly_count: number;
  high_risk_count: number;
  medium_risk_count: number;
}

/** 风险概览的 data 字段（risk_service 返回结构） */
export interface RiskOverviewResult {
  month: string;
  department_id: string;
  summary: RiskSummary;
  budget_anomalies: RiskAnomaly[];
  growth_anomalies: RiskAnomaly[];
  large_expense_anomalies: RiskAnomaly[];
}

/** 普通 risk_overview 意图的 details */
export interface RiskOverviewDetails {
  success: boolean;
  month: string;
  department_id: string;
  growth_threshold?: number;
  large_expense_threshold?: number;
  data: RiskOverviewResult;
}

/** budget-risk-review Skill 综合审查的 details */
export interface BudgetRiskReviewDetails {
  skill_name: string;
  budget_analysis: BudgetAnalysisDetails;
  risk_overview: RiskOverviewDetails;
}

/** 制度问答引用来源 */
export interface PolicySourceDetail {
  citation: string;
  chunk_id: string;
  source: string;
  document_title: string | null;
  section_title: string | null;
  similarity_score: number;
}

/** 制度问答 data 字段（policy_question_tool 返回） */
export interface PolicyQuestionData {
  query: string;
  answer: string;
  model: string;
  source_count: number;
  sources: PolicySourceDetail[];
}

/** policy_question 意图的 details */
export interface PolicyQuestionDetails {
  success: boolean;
  query: string;
  top_k?: number;
  data: PolicyQuestionData;
}

export interface AgentChatRequest {
  message: string;
  thread_id?: string | null;
}

export interface AgentChatResponse {
  thread_id: string;
  status: AgentStatus;
  requires_approval: boolean;
  approval_request: AgentApprovalRequest | null;
  answer: string;
  intent: AgentIntent;
  routing_source: string | null;
  route_reason: string | null;
  department_id: string | null;
  month: string | null;
  trace: string[];
  details: AgentDetails | null;
}
export interface AgentResumeRequest {
  thread_id: string;
  approved: boolean;
}