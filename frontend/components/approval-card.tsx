"use client";

import type { ApprovalTask } from "@/lib/types";

const ACTION_LABELS: Record<string, string> = {
  generate_budget_report: "生成预算报告",
};

const STATUS_META: Record<
  ApprovalTask["status"],
  { label: string; tone: string; hint: string }
> = {
  pending: {
    label: "需要人工确认",
    tone: "bg-blue-50 text-blue-700",
    hint: "该操作需要人工确认后才能继续",
  },
  processing: {
    label: "处理中",
    tone: "bg-zinc-100 text-zinc-600",
    hint: "正在处理，请稍候…",
  },
  approved: {
    label: "已批准",
    tone: "bg-emerald-50 text-emerald-700",
    hint: "已批准，任务已继续执行",
  },
  rejected: {
    label: "已拒绝",
    tone: "bg-zinc-100 text-zinc-600",
    hint: "操作已取消",
  },
};

interface ApprovalCardProps {
  task: ApprovalTask;
  onApprove: (task: ApprovalTask) => void;
  onReject: (task: ApprovalTask) => void;
}

export function ApprovalCard({
  task,
  onApprove,
  onReject,
}: ApprovalCardProps) {
  const status = STATUS_META[task.status];
  const actionLabel = ACTION_LABELS[task.action] ?? task.action;

  return (
    <section className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <header className="flex items-center justify-between gap-3 border-b border-zinc-100 px-5 py-3.5">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900">待审批事项</h3>
          <p className="mt-0.5 text-xs text-zinc-500">
            {task.department} 部门 · {task.month} · {actionLabel}
          </p>
        </div>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${status.tone}`}
        >
          {status.label}
        </span>
      </header>

      <div className="px-5 py-4">
        <p className="text-sm leading-6 text-zinc-700">{task.message}</p>
      </div>

      <div className="flex items-center justify-between gap-3 border-t border-zinc-100 bg-zinc-50/60 px-5 py-3">
        <span className="text-xs text-zinc-500">{status.hint}</span>
        {task.status === "pending" || task.status === "processing" ? (
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onReject(task)}
              disabled={task.status === "processing"}
              className="rounded-lg border border-zinc-300 bg-white px-3.5 py-1.5 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              拒绝
            </button>
            <button
              type="button"
              onClick={() => onApprove(task)}
              disabled={task.status === "processing"}
              className="rounded-lg bg-zinc-900 px-3.5 py-1.5 text-sm font-medium text-white transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {task.status === "processing" ? "处理中…" : "批准并生成"}
            </button>
          </div>
        ) : null}
      </div>
    </section>
  );
}

