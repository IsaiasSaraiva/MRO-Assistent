"use client";

import { Upload } from "lucide-react";
import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { uploadDocuments } from "@/lib/api";

interface UploadButtonProps {
  onUploadComplete: () => void;
}

type UploadState = "idle" | "uploading" | "success" | "error";

export function UploadButton({ onUploadComplete }: UploadButtonProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setState("uploading");
    setErrorMessage("");

    try {
      await uploadDocuments(files);
      setState("success");
      onUploadComplete();
      setTimeout(() => setState("idle"), 2000);
    } catch {
      setState("error");
      setErrorMessage("Upload failed. Please try again.");
      setTimeout(() => setState("idle"), 3000);
    } finally {
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  };

  const label: Record<UploadState, string> = {
    idle: "Upload Manual",
    uploading: "Processing...",
    success: "Uploaded!",
    error: "Upload Failed",
  };

  return (
    <div className="flex flex-col gap-1">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        multiple
        className="hidden"
        onChange={handleFileChange}
        aria-label="Select PDF files to upload"
      />
      <Button
        variant="outline"
        size="sm"
        className="w-full gap-1.5"
        onClick={handleClick}
        disabled={state === "uploading"}
      >
        <Upload className="size-3.5" />
        {label[state]}
      </Button>
      {state === "error" && (
        <p className="text-destructive text-xs" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
