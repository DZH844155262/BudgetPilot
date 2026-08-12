"use client";

import { budgetSummaryData, formatPercent, formatWan } from "@/lib/mock-data";
import type { BudgetSummaryData } from "@/lib/types";

interface MetricProps {
  label: string;
  value: string;
  accent?: boolean;
}

function Metric({ label, value, accent }: MetricProps) {
  return (
    <div className="px-3 py-3.5 first:pl-5 last:pr-5">
      <div className="text-xs text-zinc-500">{label}</div>
      <div
        className={`mt-1 text-sm font-semibold tabular-nums ${
          accent ? "text-amber-600" : "text-zinc-900"
        }`}
      >
        {value}
      </div>
    </div>
  );
}

function riskStatusTone(status?: string): string {
  if (status === "超预算") return "text-red-600";
  if (status === "预警") return "text-amber-600";
  return "text-zinc-400";
}

export function BudgetSummaryCard({
  data = budgetSummaryData,
}: {
  data?: BudgetSummaryData;
}) {
  const remaining = data.annualBudget - data.spent;
  const spentRate = data.annualBudget > 0 ? data.spent / data.annualBudget : 0;

  return (
    <section className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <header className="flex items-center justify-between gap-3 border-b border-zinc-100 px-5 py-3.5">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900">预算执行情况</h3>
          <p className="mt-0.5 text-xs text-zinc-500">
            {data.department} · {data.period}
          </p>
        </div>
        <span className="shrink-0 rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600">
          预算执行分析
        </span>
      </header>

      <div className="grid grid-cols-4 divide-x divide-zinc-100 border-b border-zinc-100">
        <Metric label="总预算" value={formatWan(data.annualBudget)} />
        <Metric label="总支出" value={formatWan(data.spent)} />
        <Metric
          label="剩余预算"
          value={formatWan(remaining)}
          accent={remaining < 0}
        />
        <Metric
          label="执行率"
          value={formatPercent(data.spent, data.annualBudget)}
          accent={spentRate >= 0.8}
        />
      </div>

      <div className="space-y-4 px-5 py-4">
        {data.categories.map((category) => {
          const rate =
            category.budget > 0 ? category.spent / category.budget : 0;
          const barWidth = `${Math.min(Math.round(rate * 1000) / 10, 100)}%`;
          const tone =
            rate >= 0.9 ? "bg-red-500" : rate >= 0.75 ? "bg-amber-500" : "bg-zinc-900";
          const hint =
            category.riskStatus ??
            (rate >= 0.9
              ? "接近预算上限"
              : rate >= 0.75
                ? "执行较快"
                : "进度正常");

          return (
            <div key={category.name}>
              <div className="flex items-baseline justify-between gap-4">
                <span className="text-sm font-medium text-zinc-800">
                  {category.name}
                </span>
                <span className="text-xs tabular-nums text-zinc-500">
                  {formatWan(category.spent)} / {formatWan(category.budget)}
                </span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-zinc-100">
                <div
                  className={`h-full rounded-full ${tone}`}
                  style={{ width: barWidth }}
                />
              </div>
              <div className="mt-1.5 flex items-center justify-between">
                <span className="text-xs text-zinc-400">
                  执行率 {formatPercent(category.spent, category.budget)}
                </span>
                <span className={`text-xs ${riskStatusTone(category.riskStatus)}`}>
                  {hint}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <footer className="flex items-center justify-between gap-3 border-t border-zinc-100 bg-zinc-50/60 px-5 py-2.5 text-xs text-zinc-500">
        <span>
          {data.commitment > 0
            ? `含已承诺未付款 ${formatWan(data.commitment)}，综合执行率 ${formatPercent(data.spent + data.commitment, data.annualBudget)}`
            : `总剩余预算 ${formatWan(remaining)}`}
        </span>
        <span className="shrink-0">统计期间：{data.period}</span>
      </footer>
    </section>
  );
}

