import type {
  BudgetSummaryData,
  CapabilityItem,
  ConversationItem,
  Message,
  PolicySource,
  RiskOverviewData,
  SuggestedAction,
} from "./types";

export const recentConversations: ConversationItem[] = [
  { id: "c1", title: "研发部 2026-07 预算执行分析", updatedAt: "今天 09:24" },
  { id: "c2", title: "Q2 差旅费用合规审查", updatedAt: "昨天 17:40" },
  { id: "c3", title: "市场部年中预算调整建议", updatedAt: "07-28 14:12" },
  { id: "c4", title: "设备采购审批流程查询", updatedAt: "07-25 10:03" },
];

export const capabilities: CapabilityItem[] = [
  {
    id: "cap1",
    label: "预算执行分析",
    description: "部门预算执行进度与偏差",
    icon: "trend",
  },
  {
    id: "cap2",
    label: "风险异常检测",
    description: "超支、异常与合规风险",
    icon: "shield",
  },
  {
    id: "cap3",
    label: "企业制度问答",
    description: "报销、审批等制度依据",
    icon: "book",
  },
  {
    id: "cap4",
    label: "预算报告生成",
    description: "自动生成结构化分析报告",
    icon: "report",
  },
];

export const suggestedActions: SuggestedAction[] = [
  {
    id: "s1",
    label: "查看预算执行",
    prompt: "帮我看看研发部2026-07的预算执行情况",
  },
  {
    id: "s2",
    label: "综合风险审查",
    prompt: "帮我全面审查研发部2026-07的预算风险",
  },
  {
    id: "s3",
    label: "查询审批制度",
    prompt: "单笔费用达到50000元需要谁审批？",
  },
];

export const budgetSummaryData: BudgetSummaryData = {
  department: "研发部",
  period: "2026-07",
  annualBudget: 12000000,
  spent: 7342000,
  commitment: 1050000,
  categories: [
    { name: "人力外包", budget: 4200000, spent: 3180000 },
    { name: "设备采购", budget: 3000000, spent: 1820000 },
    { name: "差旅费", budget: 1800000, spent: 1294000 },
    { name: "办公及杂费", budget: 1500000, spent: 648000 },
    { name: "其他", budget: 1500000, spent: 400000 },
  ],
};

export const riskOverviewData: RiskOverviewData = {
  department: "研发部",
  period: "2026-07",
  riskCount: 5,
  highCount: 1,
  mediumCount: 2,
  lowCount: 2,
  risks: [
    {
      id: "r1",
      severity: "high",
      title: "设备采购预算预计超支 12%",
      description:
        "「高性能计算集群」项目已签合同 860 万，超出该项目预算 92 万，需关注后续付款进度。",
      status: "待处理",
    },
    {
      id: "r2",
      severity: "medium",
      title: "差旅费支出节奏偏快",
      description:
        "7 月差旅支出 129.4 万，累计执行率 71.9%，高于时间进度 14 个百分点，存在季度末超支风险。",
      status: "待处理",
    },
    {
      id: "r3",
      severity: "medium",
      title: "存在超审批权限报销单",
      description:
        "3 笔报销单金额超过部门主管审批权限，尚未完成补充审批流程。",
      status: "待处理",
    },
    {
      id: "r4",
      severity: "low",
      title: "预算科目间调剂 2 次",
      description:
        "本月发生预算科目调剂 2 次，均已完成线上审批，建议关注调剂频率。",
      status: "已记录",
    },
    {
      id: "r5",
      severity: "low",
      title: "供应商集中度偏高",
      description:
        "前三大供应商合同金额占比 41%，建议在后续采购中分散供应商风险。",
      status: "已记录",
    },
  ],
};

export const policySources: PolicySource[] = [
  {
    id: "p1",
    title: "预算审批权限管理规定",
    section: "第四章 审批权限 · 4.2",
    summary:
      "单笔支出或合同付款 50 万元（含）以上，须经 CFO 审批；100 万元（含）以上须经 CEO 审批。",
    snippet:
      "4.2.1 单笔金额 5 万~50 万元（不含）：由部门负责人及分管 VP 审批；4.2.2 单笔金额 50 万元（含）以上：由 CFO 审批……",
    updatedAt: "2026-05 修订",
  },
  {
    id: "p2",
    title: "费用报销管理办法",
    section: "第三章 报销流程 · 3.5",
    summary:
      "超过审批权限的报销单应自动进入上一级审批流，并抄送财务复核岗。",
    snippet:
      "3.5.2 报销金额超出直接上级权限时，系统自动路由至有权审批人，并同步抄送财务部复核岗位……",
    updatedAt: "2026-01 修订",
  },
];

export const initialMessages: Message[] = [
  {
    id: "m0",
    role: "assistant",
    content:
      "你好，我是 BudgetPilot 预算智能助手。我可以帮你分析预算执行情况、识别预算风险、查询企业审批制度，或者生成预算分析报告。今天想先看哪个部门？",
  },
];

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 0,
  }).format(value);
}

/** 将金额格式化为「万元」 */
export function formatWan(value: number): string {
  const wan = value / 10000;
  const text = Number.isInteger(wan)
    ? wan.toLocaleString("zh-CN")
    : wan.toFixed(1);
  return `${text} 万`;
}

export function formatPercent(part: number, total: number): string {
  if (total === 0) return "0%";
  return `${Math.round((part / total) * 1000) / 10}%`;
}
