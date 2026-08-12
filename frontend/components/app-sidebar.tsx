"use client";

import type { ComponentType, SVGProps } from "react";
import type { CapabilityItem, ConversationItem } from "@/lib/types";
import {
  BookIcon,
  LogoMark,
  MessageIcon,
  PlusIcon,
  ReportIcon,
  ShieldIcon,
  SparkleIcon,
  TrendIcon,
} from "./icons";

type CapabilityIconName = CapabilityItem["icon"];

const capabilityIcons: Record<
  CapabilityIconName,
  ComponentType<SVGProps<SVGSVGElement>>
> = {
  trend: TrendIcon,
  shield: ShieldIcon,
  book: BookIcon,
  report: ReportIcon,
};

interface AppSidebarProps {
  conversations: ConversationItem[];
  capabilities: CapabilityItem[];
  activeConversationId?: string;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
}

export function AppSidebar({
  conversations,
  capabilities,
  activeConversationId,
  onNewChat,
  onSelectConversation,
}: AppSidebarProps) {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-zinc-200 bg-white lg:flex">
      {/* 品牌区 */}
      <div className="flex items-center gap-2.5 px-5 pb-5 pt-6">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-zinc-900 text-white">
          <LogoMark className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <div className="text-sm font-semibold tracking-tight text-zinc-900">
            BudgetPilot
          </div>
          <div className="text-xs text-zinc-500">企业预算智能助手</div>
        </div>
      </div>

      {/* 新建会话 */}
      <div className="px-4 pb-4">
        <button
          type="button"
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-50 hover:text-zinc-900"
        >
          <PlusIcon className="h-4 w-4" />
          新建会话
        </button>
      </div>

      {/* 最近会话 + 核心能力 */}
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="px-1 pb-2 pt-1 text-xs font-medium uppercase tracking-wider text-zinc-400">
          最近会话
        </div>
        <div className="space-y-0.5">
          {conversations.map((conversation) => {
            const isActive = conversation.id === activeConversationId;
            return (
              <button
                key={conversation.id}
                type="button"
                onClick={() => onSelectConversation(conversation.id)}
                className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left transition-colors ${
                  isActive ? "bg-zinc-100" : "hover:bg-zinc-50"
                }`}
              >
                <MessageIcon
                  className={`h-4 w-4 shrink-0 ${
                    isActive ? "text-zinc-700" : "text-zinc-400"
                  }`}
                />
                <span
                  className={`min-w-0 flex-1 truncate text-sm ${
                    isActive ? "font-medium text-zinc-900" : "text-zinc-600"
                  }`}
                >
                  {conversation.title}
                </span>
                <span className="shrink-0 text-[11px] text-zinc-400">
                  {conversation.updatedAt}
                </span>
              </button>
            );
          })}
        </div>

        <div className="px-1 pb-2 pt-6 text-xs font-medium uppercase tracking-wider text-zinc-400">
          核心能力
        </div>
        <div className="space-y-0.5">
          {capabilities.map((capability) => {
            const Icon = capabilityIcons[capability.icon];
            return (
              <button
                key={capability.id}
                type="button"
                className="group flex w-full items-start gap-2.5 rounded-lg px-2.5 py-2 text-left transition-colors hover:bg-zinc-50"
              >
                <Icon className="mt-0.5 h-4 w-4 shrink-0 text-zinc-500 group-hover:text-zinc-700" />
                <span className="min-w-0">
                  <span className="block text-sm font-medium text-zinc-800">
                    {capability.label}
                  </span>
                  <span className="block text-xs leading-5 text-zinc-500">
                    {capability.description}
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Agent 状态 */}
      <div className="px-4 pb-4">
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 px-3.5 py-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            <span className="flex items-center gap-1.5 text-sm font-medium text-zinc-800">
              <SparkleIcon className="h-3.5 w-3.5 text-zinc-500" />
              Agent 在线
            </span>
          </div>
          <p className="mt-1 text-xs leading-5 text-zinc-500">
            预算智能体已就绪，可随时发起分析。
          </p>
        </div>
      </div>
    </aside>
  );
}
