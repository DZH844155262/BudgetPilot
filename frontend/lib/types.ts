export type MessageRole = "user" | "assistant";

/** Agent 可渲染的结构化卡片类型 */
export type CardKind =
  | "budget-summary"
  | "risk-overview"
  | "approval"
  | "policy-source";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  /** 卡片上方的轻量标签（例如 Skill 名称） */
  heading?: string;
  /** 该消息附带的结构化卡片及数据 */
  cards?: MessageCard[];
  /** 待人工确认的审批任务（HITL） */
  approval?: ApprovalTask;
}

/** 带数据的结构化卡片 */
export type MessageCard =
  | { kind: "budget-summary"; data: BudgetSummaryData }
  | { kind: "risk-overview"; data: RiskOverviewData }
  | { kind: "approval"; data: ApprovalTask }
  | { kind: "policy-source"; data: PolicySource[] };

export interface ConversationItem {
  id: string;
  title: string;
  updatedAt: string;
}

export interface CapabilityItem {
  id: string;
  label: string;
  description: string;
  icon: "trend" | "shield" | "book" | "report";
}

export interface SuggestedAction {
  id: string;
  label: string;
  prompt: string;
}

export interface BudgetCategory {
  name: string;
  budget: number;
  spent: number;
  /** 后端返回的预算风险状态：正常 / 预警 / 超预算 */
  riskStatus?: string;
}

export interface BudgetSummaryData {
  department: string;
  period: string;
  annualBudget: number;
  spent: number;
  /** 已承诺但尚未付款的金额 */
  commitment: number;
  categories: BudgetCategory[];
}

export type RiskSeverity = "high" | "medium" | "low";

/** 风险条目来源分组 */
export type RiskGroup = "budget" | "growth" | "large_expense";

export interface RiskGroupSummary {
  key: RiskGroup;
  label: string;
  count: number;
}

export interface RiskItem {
  id: string;
  severity: RiskSeverity;
  title: string;
  description: string;
  status: string;
  group?: RiskGroup;
}

export interface RiskOverviewData {
  department: string;
  period: string;
  riskCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  risks: RiskItem[];
  /** 分组统计：预算异常 / 环比异常 / 大额费用 */
  groups?: RiskGroupSummary[];
}

/** 审批任务状态 */
export type ApprovalStatus =
  | "pending"
  | "processing"
  | "approved"
  | "rejected";

/** HITL 人工审批任务（例如预算报告生成前的人工确认） */
export interface ApprovalTask {
  /** 唯一标识，使用 thread_id */
  id: string;
  /** 后端 approval_request.action */
  action: string;
  department: string;
  month: string;
  message: string;
  status: ApprovalStatus;
  /** 用于 /agent/resume 恢复执行的会话 ID */
  threadId: string;
}

export interface PolicySource {
  id: string;
  title: string;
  section?: string;
  summary?: string;
  snippet?: string;
  updatedAt?: string;
  /** 来源文件路径/文件名 */
  path?: string;
  /** 语义相似度（0~1） */
  similarity?: number;
}
