"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { resetPassword } from "@/lib/api"; // vamos criar essa função no api.ts

export default function ResetPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      await resetPassword(email, newPassword);
      setSuccess("Password updated successfully! Redirecting to login...");
      setTimeout(() => router.push("/login"), 2000);
    } catch (err: any) {
      if (err?.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Failed to reset password");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-dvh w-screen items-center justify-center bg-background">
      <div className="flex w-full max-w-sm flex-col gap-8 rounded-2xl border bg-card p-8 shadow-sm">
        <div className="flex flex-col items-center gap-4">
          <Image
            src="/MRO.png"
            alt="MRO Assistant logo"
            width={80}
            height={80}
            priority
            className="rounded-lg"
          />
          <div className="text-center">
            <h1 className="font-semibold text-xl">MRO Assistant</h1>
            <p className="mt-1 text-muted-foreground text-sm">
              Insira seu email e nova senha para recuperar o acesso à sua conta.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="new-password" className="text-sm font-medium">
              Nova Senha
            </label>
            <Input
              id="new-password"
              type="password"
              placeholder="••••••••"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          {error && (
            <p className="text-destructive text-sm" role="alert">
              {error}
            </p>
          )}
          {success && (
            <p className="text-green-500 text-sm" role="alert">
              {success}
            </p>
          )}

          <Button type="submit" disabled={isLoading} className="w-full cursor-pointer">
            {isLoading ? "Updating password..." : "Atualizar Senha"}
          </Button>
        </form>
      </div>
    </div>
  );
}