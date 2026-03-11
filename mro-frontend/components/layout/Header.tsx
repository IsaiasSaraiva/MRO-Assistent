"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { clearToken, decodeToken, getToken } from "@/lib/auth";

export function Header() {
  const router = useRouter();
  const [userName, setUserName] = useState<string>("");

  useEffect(() => {
    const token = getToken();
    if (token) {
      const payload = decodeToken(token);
      if (payload?.name) {
        setUserName(payload.name);
      }
    }
  }, []);

  const handleLogout = () => {
    clearToken();
    router.push("/login");
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex h-14 items-center justify-between border-b bg-background px-4">
      <div className="flex items-center gap-2">
        <Image
          src="/MRO.png"
          alt="MRO Assistant logo"
          width={32}
          height={32}
          className="rounded"
        />
        <span className="font-semibold text-sm">MRO Assistant</span>
      </div>
      <div className="flex items-center gap-3">
        {userName && (
          <span className="text-muted-foreground text-sm">{userName}</span>
        )}
        <Button variant="outline" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}
