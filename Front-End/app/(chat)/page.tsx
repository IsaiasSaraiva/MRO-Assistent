"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { sendMessage, downloadReportPDF } from "@/lib/api";

interface Source {
  filename: string;
  page?: number;
  excerpt: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  is_report?: boolean;
}

export default function ChatPage() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [downloadingIndex, setDownloadingIndex] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("mro_token");
    if (!token) {
      router.replace("/login"); // replace em vez de push — não adiciona no histórico
    } else {
      setAuthenticated(true);
    }
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (question: string) => {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsLoading(true);
    try {
      const data = await sendMessage(question);

      if (data.formulario015 && data.pdf_base64) {
        const bytes = atob(data.pdf_base64);
        const arr = new Uint8Array(bytes.length);
        for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
        const blob = new Blob([arr], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = data.filename || "formulario_015.pdf";
        a.click();
        URL.revokeObjectURL(url);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          is_report: data.is_report,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "An error occurred while processing your request. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (content: string, index: number) => {
    setDownloadingIndex(index);
    try {
      await downloadReportPDF(content, `relatorio_mro_${index + 1}.pdf`);
    } catch {
      alert("Erro ao gerar PDF. Tente novamente.");
    } finally {
      setDownloadingIndex(null);
    }
  };

  // null = ainda verificando | false = não autenticado | true = autenticado
  if (authenticated === null) return (
    <div className="flex h-full items-center justify-center">
      <span className="text-muted-foreground text-sm">Carregando...</span>
    </div>
  );

  if (!authenticated) return null;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
            Ask a question about your indexed maintenance manuals.
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className="flex flex-col gap-2">
            <MessageBubble
              role={msg.role}
              content={msg.content}
              sources={msg.sources}
            />
            {msg.role === "assistant" && msg.is_report && (
              <div className="flex justify-start pl-2">
                <button
                  onClick={() => handleDownload(msg.content, i)}
                  disabled={downloadingIndex === i}
                  className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-md border border-border bg-background hover:bg-accent text-foreground transition-colors disabled:opacity-50"
                >
                  {downloadingIndex === i ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      Gerando PDF...
                    </>
                  ) : (
                    <>📥 Baixar Relatório em PDF</>
                  )}
                </button>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <span className="flex gap-1">
              <span className="animate-bounce [animation-delay:0ms]">.</span>
              <span className="animate-bounce [animation-delay:150ms]">.</span>
              <span className="animate-bounce [animation-delay:300ms]">.</span>
            </span>
            <span>Thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t bg-background p-4">
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}