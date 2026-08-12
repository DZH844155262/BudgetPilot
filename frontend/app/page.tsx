"use client";

import { useEffect, useRef, useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { ChatInput } from "@/components/chat-input";
import { ChatMessage } from "@/components/chat-message";
import { SuggestedActions } from "@/components/suggested-actions";
import { LogoMark } from "@/components/icons";
import { ApiError, resumeAgentTask, sendAgentMessage } from "@/lib/api";
import {
  buildApprovalTask,
  buildDisplayAnswer,
  mapDetailsToCards,
} from "@/lib/details-mapper";
import {
  capabilities,
  initialMessages,
  recentConversations,
  suggestedActions,
} from "@/lib/mock-data";
import type { Message } from "@/lib/types";

const FALLBACK_ERROR_MESSAGE =
  "请求暂时失败，请确认 BudgetPilot 后端服务是否正常运行。";

/** 仅展示安全的错误说明，不暴露堆栈或敏感配置 */
function buildErrorMessage(error: unknown): string {
  if (error instanceof ApiError && error.message) {
    return `请求暂时失败：${error.message}`;
  }
  return FALLBACK_ERROR_MESSAGE;
}

function LoadingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-zinc-900 text-white">
        <LogoMark className="h-4 w-4" />
      </div>
      <div className="rounded-2xl border border-zinc-200 bg-white px-4 py-3 text-sm text-zinc-500">
        BudgetPilot 正在分析…
      </div>
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [activeConversationId, setActiveConversationId] = useState<
    string | undefined
  >(recentConversations[0]?.id);
  const idRef = useRef(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const requestSeqRef = useRef(0);

  useEffect(() => {
    const container = scrollRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  function nextId(): string {
    idRef.current += 1;
    return `msg-${Date.now()}-${idRef.current}`;
  }

  function handleSubmit(raw?: string) {
    const content = (raw ?? input).trim();
    if (!content || loading) {
      return;
    }

    const requestSeq = requestSeqRef.current + 1;
    requestSeqRef.current = requestSeq;

    setMessages((current) => [
      ...current,
      { id: nextId(), role: "user", content },
    ]);
    setInput("");
    setLoading(true);

    sendAgentMessage({ message: content, thread_id: threadId })
      .then((response) => {
        if (requestSeqRef.current !== requestSeq) {
          return;
        }
        const mapping = mapDetailsToCards(response);
        const approvalTask = buildApprovalTask(response);
        setMessages((current) => [
          ...current,
          {
            id: nextId(),
            role: "assistant",
            content: buildDisplayAnswer(response, mapping),
            heading: mapping.heading,
            cards: mapping.cards,
            approval: approvalTask ?? undefined,
          },
        ]);
        setThreadId(response.thread_id);
      })
      .catch((error: unknown) => {
        if (requestSeqRef.current !== requestSeq) {
          return;
        }
        setMessages((current) => [
          ...current,
          {
            id: nextId(),
            role: "assistant",
            content: buildErrorMessage(error),
          },
        ]);
      })
      .finally(() => {
        if (requestSeqRef.current === requestSeq) {
          setLoading(false);
        }
      });
  }

  /** 处理审批按钮：批准/拒绝后调用 /agent/resume 恢复任务 */
  function handleResolveApproval(message: Message, approved: boolean) {
    const approval = message.approval;
    if (!approval || approval.status === "processing") {
      return;
    }

    setMessages((current) =>
      current.map((item) =>
        item.id === message.id && item.approval
          ? { ...item, approval: { ...item.approval, status: "processing" } }
          : item,
      ),
    );

    resumeAgentTask({ thread_id: approval.threadId, approved })
      .then((response) => {
        const mapping = mapDetailsToCards(response);
        const finalMessage: Message = {
          id: nextId(),
          role: "assistant",
          content: buildDisplayAnswer(response, mapping),
          heading: mapping.heading,
          cards: mapping.cards,
        };
        const nextStatus: "approved" | "rejected" = approved
          ? "approved"
          : "rejected";
        setMessages((current) => [
          ...current.map((item) =>
            item.id === message.id && item.approval
              ? {
                  ...item,
                  approval: { ...item.approval, status: nextStatus },
                }
              : item,
          ),
          finalMessage,
        ]);
        setThreadId(response.thread_id);
      })
      .catch((error: unknown) => {
        setMessages((current) => [
          ...current.map((item) =>
            item.id === message.id && item.approval
              ? { ...item, approval: { ...item.approval, status: "pending" as const } }
              : item,
          ),
          {
            id: nextId(),
            role: "assistant",
            content: buildErrorMessage(error),
          },
        ]);
      });
  }

  function handleNewChat() {
    requestSeqRef.current += 1;
    setMessages([...initialMessages]);
    setActiveConversationId(undefined);
    setThreadId(null);
    setLoading(false);
  }

  const activeConversation = recentConversations.find(
    (item) => item.id === activeConversationId,
  );

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-50 text-zinc-900">
      <AppSidebar
        conversations={recentConversations}
        capabilities={capabilities}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={setActiveConversationId}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        {/* Header */}
        <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-zinc-200 bg-white px-6">
          <div className="min-w-0">
            <h1 className="truncate text-sm font-semibold text-zinc-900">
              {activeConversation?.title ?? "新会话"}
            </h1>
            <p className="mt-0.5 text-xs text-zinc-500">
              {activeConversation
                ? "预算执行分析 · 风险审查 · 制度问答"
                : "输入问题，开始与预算智能体对话"}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1.5 text-xs font-medium text-zinc-600">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Agent 已连接
          </div>
        </header>

        {/* 消息区 */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-3xl px-6 py-8">
            <div className="space-y-8">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onResolveApproval={handleResolveApproval}
                />
              ))}
              {loading ? <LoadingIndicator /> : null}
            </div>
          </div>
        </div>

        {/* 快捷操作 + 输入区 */}
        <div className="shrink-0 border-t border-zinc-200 bg-white/70">
          <div className="mx-auto w-full max-w-3xl space-y-3 px-6 py-4">
            <SuggestedActions
              actions={suggestedActions}
              onSelect={(prompt) => handleSubmit(prompt)}
            />
            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleSubmit();
              }}
              className="space-y-2"
            >
              <ChatInput
                value={input}
                onChange={setInput}
                onSubmit={() => handleSubmit()}
                disabled={loading}
              />
              <p className="text-center text-xs text-zinc-400">
                BudgetPilot 的分析结果以企业业务数据与制度知识库为依据
              </p>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
