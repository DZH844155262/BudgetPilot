"use client";

import type { SuggestedAction } from "@/lib/types";

interface SuggestedActionsProps {
  actions: SuggestedAction[];
  onSelect: (prompt: string) => void;
}

export function SuggestedActions({
  actions,
  onSelect,
}: SuggestedActionsProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium text-zinc-400">快捷操作</span>
      {actions.map((action) => (
        <button
          key={action.id}
          type="button"
          onClick={() => onSelect(action.prompt)}
          className="rounded-full border border-zinc-200 bg-white px-3.5 py-1.5 text-sm text-zinc-700 transition-colors hover:border-zinc-300 hover:bg-zinc-50 hover:text-zinc-900"
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
