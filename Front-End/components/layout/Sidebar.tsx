"use client";

import { DocumentList } from "@/components/documents/DocumentList";
import { UploadButton } from "@/components/documents/UploadButton";
import { Button } from "@/components/ui/button";
import { clearCollection } from "@/lib/api";
import { useState } from "react";

export function Sidebar() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [isClearing, setIsClearing] = useState(false);

  const handleRefresh = () => setRefreshKey((k) => k + 1);

  const handleClearAll = async () => {
    if (!window.confirm("Tem certeza que deseja excluir todos os documentos? ")) {
      return;
    }
    setIsClearing(true);
    try {
      await clearCollection();
      handleRefresh();
    } catch {
      // no-op — documents will still show if clear failed
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <aside className="fixed top-14 left-0 bottom-0 z-40 flex w-64 flex-col border-r bg-background">
      <div className="flex flex-col gap-2 border-b p-3">
        <p className="font-medium text-sm">Documentos (Relatórios e Manuais)</p>
        <UploadButton onUploadComplete={handleRefresh} />
      </div>
      <div className="flex-1 overflow-y-auto">
        <DocumentList refreshKey={refreshKey} onRefresh={handleRefresh} />
      </div>
      <div className="border-t p-3">
        <Button
          variant="destructive"
          size="sm"
          className="w-full"
          onClick={handleClearAll}
          disabled={isClearing}
        >
          {isClearing ? "Clearing..." : "Exluir Todos os Documentos"}
        </Button>
      </div>
    </aside>
  );
}
