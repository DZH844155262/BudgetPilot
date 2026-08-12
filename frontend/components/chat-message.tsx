"use client";

import type { Message } from "@/lib/types";
import { LogoMark } from "./icons";
import { BudgetSummaryCard } from "./budget-summary-card";
import { RiskOverviewCard } from "./risk-overview-card";
import { ApprovalCard } from "./approval-card";
import { PolicySourceCard } from "./policy-source-card";

interface ChatMessageProps {
  message: Message;
  /** 审批按钮回调（true=批准，false=拒绝） */
  onResolveApproval?: (message: Message, approved: boolean) => void;
}

export function ChatMessage({
  message,
  onResolveApproval,
}: ChatMessageProps) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-zinc-900 px-4 py-2.5 text-sm leading-6 text-white">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-zinc-900 text-white">
        <LogoMark className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1 space-y-3">
        {message.content ? (
          <p className="text-sm leading-6 text-zinc-800">{message.content}</p>
        ) : null}
        {message.heading ? (
          <span className="inline-flex w-fit items-center rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-medium text-zinc-600">
            {message.heading}
          </span>
        ) : null}
        {message.approval && onResolveApproval ? (
          <ApprovalCard
            task={message.approval}
            onApprove={() => onResolveApproval(message, true)}
            onReject={() => onResolveApproval(message, false)}
          />
        ) : null}
        {message.cards?.map((card) => {
          switch (card.kind) {
            case "budget-summary":
              return <BudgetSummaryCard key={card.kind} data={card.data} />;
            case "risk-overview":
              return <RiskOverviewCard key={card.kind} data={card.data} />;
            case "approval":
              return onResolveApproval ? (
                <ApprovalCard
                  key={card.kind}
                  task={card.data}
                  onApprove={() => onResolveApproval(message, true)}
                  onReject={() => onResolveApproval(message, false)}
                />
              ) : null;
            case "policy-source":
              return <PolicySourceCard key={card.kind} sources={card.data} />;
          }
        })}
      </div>
    </div>
  );
}
