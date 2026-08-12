"use client";

import { riskOverviewData } from "@/lib/mock-data";
import type { RiskOverviewData, RiskSeverity } from "@/lib/types";

const severityStyles: Record<
  RiskSeverity,
  { badge: string; label: string }
> = {
  high: { badge: "bg-red-50 text-red-700", label: "高风险" },
  medium: { badge: "bg-amber-50 text-amber-700", label: "中风险" },
  low: { badge: "bg-zinc-100 text-zinc-600", label: "低风险" },
};

export function RiskOverviewCard({
  data = riskOverviewData,
}: {
  data?: RiskOverviewData;
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-100 px-5 py-3.5">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900">
            风险与异常检测
          </h3>
          <p className="mt-0.5 text-xs text-zinc-500">
            {data.department} · {data.period} 预算扫描
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
            高风险 {data.highCount}
          </span>
          <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
            中风险 {data.mediumCount}
          </span>
          <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600">
            低风险 {data.lowCount}
          </span>
        </div>
      </header>

      {data.groups && data.groups.length > 0 ? (
        <div className="flex flex-wrap items-center gap-1.5 border-b border-zinc-100 px-5 py-2.5">
          {data.groups.map((group) => (
            <span
              key={group.key}
              className="rounded-full bg-zinc-100 px-2.5 py-0.5 text-[11px] font-medium text-zinc-600"
            >
              {group.label} {group.count}
            </span>
          ))}
        </div>
      ) : null}

      <ul className="divide-y divide-zinc-100">
        {data.risks.map((risk) => {
          const style = severityStyles[risk.severity];
          return (
            <li key={risk.id} className="flex gap-3.5 px-5 py-4">
              <span
                className={`mt-0.5 flex h-5 shrink-0 items-center rounded-full px-2 text-[11px] font-medium ${style.badge}`}
              >
                {style.label}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <span className="text-sm font-medium text-zinc-900">
                    {risk.title}
                  </span>
                  <span className="shrink-0 text-[11px] text-zinc-400">
                    {risk.status}
                  </span>
                </div>
                <p className="mt-1 text-sm leading-6 text-zinc-600">
                  {risk.description}
                </p>
              </div>
            </li>
          );
        })}
      </ul>

      <footer className="border-t border-zinc-100 bg-zinc-50/60 px-5 py-2.5 text-xs text-zinc-500">
        共发现 {data.riskCount} 项风险与异常，建议优先处理 {data.highCount}{" "}
        项高风险事项。
      </footer>
    </section>
  );
}
