"use client";

import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { deleteDocument, getDocuments } from "@/lib/api";

interface Document {
  id: string;
  filename: string;
  chunk_count: number;
  uploaded_at: string;
}

interface DocumentListProps {
  refreshKey: number;
  onRefresh: () => void;
}

export function DocumentList({ refreshKey, onRefresh }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    getDocuments()
      .then((data) => {
        if (!cancelled) setDocuments(data);
      })
      .catch(() => {
        if (!cancelled) setDocuments([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteDocument(id);
      onRefresh();
    } catch {
      // no-op — list stays intact if delete fails
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 p-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-10 w-full rounded-md" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <p className="p-4 text-center text-muted-foreground text-xs">
        No documents indexed yet.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-1 p-2">
      {documents.map((doc) => (
        <li
          key={doc.id}
          className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 hover:bg-accent"
        >
          <div className="min-w-0 flex-1">
            <p
              className="truncate text-xs font-medium"
              title={doc.filename}
            >
              {doc.filename}
            </p>
            <p className="text-muted-foreground text-xs">
              {doc.chunk_count} chunks
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            aria-label={`Delete ${doc.filename}`}
            disabled={deletingId === doc.id}
            onClick={() => handleDelete(doc.id)}
          >
            <Trash2 className="size-3.5" />
          </Button>
        </li>
      ))}
    </ul>
  );
}
