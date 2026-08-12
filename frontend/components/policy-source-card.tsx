"use client";

import { policySources } from "@/lib/mock-data";
import type { PolicySource } from "@/lib/types";
import { BookIcon } from "./icons";

export function PolicySourceCard({
  sources = policySources,
}: {
  sources?: PolicySource[];
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <header className="border-b border-zinc-100 px-5 py-3">
        <h3 className="text-sm font-semibold text-zinc-900">制度依据</h3>
        <p className="mt-0.5 text-xs text-zinc-500">
          来源：企业制度知识库 · 已检索 {sources.length} 条
        </p>
      </header>

      <ul className="divide-y divide-zinc-100">
        {sources.map((source) => (
          <li key={source.id} className="px-5 py-3.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <BookIcon className="h-4 w-4 shrink-0 text-zinc-400" />
                <span className="text-sm font-medium text-zinc-900">
                  {source.title}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-1.5">
                {source.section ? (
                  <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] text-zinc-500">
                    {source.section}
                  </span>
                ) : null}
                {typeof source.similarity === "number" ? (
                  <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] tabular-nums text-zinc-500">
                    相似度 {source.similarity.toFixed(2)}
                  </span>
                ) : null}
              </div>
            </div>

            {source.summary ? (
              <p className="mt-2 text-sm leading-6 text-zinc-700">
                {source.summary}
              </p>
            ) : null}

            {source.snippet ? (
              <blockquote className="mt-2 border-l-2 border-zinc-200 pl-3 text-xs leading-5 text-zinc-500">
                “{source.snippet}”
              </blockquote>
            ) : null}

            {source.path || source.updatedAt ? (
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-zinc-400">
                {source.path ? <span>{source.path}</span> : null}
                {source.updatedAt ? (
                  <span>修订时间：{source.updatedAt}</span>
                ) : null}
              </div>
            ) : null}
          </li>
        ))}
      </ul>

      <footer className="border-t border-zinc-100 bg-zinc-50/60 px-5 py-2.5 text-xs text-zinc-500">
        回答由企业制度知识库生成，仅供参考，正式依据以最新制度文件为准。
      </footer>
    </section>
  );
}

