import { cn } from "@/lib/utils";
import { SourceCard } from "@/components/chat/SourceCard";

interface Source {
  filename: string;
  page?: number;
  excerpt: string;
}

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export function MessageBubble({ role, content, sources }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-muted text-foreground"
        )}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-2 flex flex-col gap-1">
            <p className="text-xs text-muted-foreground font-medium">Sources:</p>
            {sources.map((source, i) => (
              <SourceCard
                key={i}
                filename={source.filename}
                page={source.page}
                excerpt={source.excerpt}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
