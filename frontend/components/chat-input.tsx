"use client";

import type { KeyboardEvent } from "react";
import { SendIcon } from "./icons";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

export function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
}: ChatInputProps) {
  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (disabled) {
      return;
    }
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <div className="rounded-2xl border border-zinc-300 bg-white shadow-sm transition-colors focus-within:border-zinc-500">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        rows={2}
        placeholder="输入你的问题，例如：帮我分析研发部 7 月份的预算风险"
        className="max-h-44 min-h-[72px] w-full resize-none bg-transparent px-4 pb-1 pt-3 text-sm leading-6 text-zinc-900 outline-none placeholder:text-zinc-400"
      />
      <div className="flex items-center justify-between px-3 pb-2.5">
        <span className="text-[11px] text-zinc-400">
          {disabled
            ? "BudgetPilot 正在分析…"
            : "Enter 发送 · Shift + Enter 换行"}
        </span>
        <button
          type="button"
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
          className="flex h-8 items-center gap-1.5 rounded-lg bg-zinc-900 px-3 text-sm font-medium text-white transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-30"
        >
          <SendIcon className="h-4 w-4" />
          发送
        </button>
      </div>
    </div>
  );
}
