import type {
  AgentChatRequest,
  AgentChatResponse,
  AgentResumeRequest,
} from "./api-types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function getErrorMessage(
  response: Response,
): Promise<string> {
  try {
    const data = await response.json();

    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }
  } catch {
    // 非JSON错误响应使用通用错误
  }

  return `请求失败，HTTP状态码：${response.status}`;
}

export async function sendAgentMessage(
  payload: AgentChatRequest,
): Promise<AgentChatResponse> {
  const response = await fetch(
    `${API_BASE_URL}/agent/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new ApiError(
      message,
      response.status,
    );
  }

  return (
    await response.json()
  ) as AgentChatResponse;
}
export async function resumeAgentTask(
  payload: AgentResumeRequest,
): Promise<AgentChatResponse> {
  const response = await fetch(
    `${API_BASE_URL}/agent/resume`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    const message =
      await getErrorMessage(response);

    throw new ApiError(
      message,
      response.status,
    );
  }

  return (
    await response.json()
  ) as AgentChatResponse;
}