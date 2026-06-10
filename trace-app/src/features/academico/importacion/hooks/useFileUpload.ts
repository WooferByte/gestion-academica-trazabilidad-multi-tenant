import { useState, useCallback } from "react";
import type { UploadState } from "@/features/academico/types";

interface UseFileUploadReturn {
  state: UploadState;
  error: string | null;
  fileToken: string | null;
  setState: (s: UploadState) => void;
  setError: (e: string | null) => void;
  setFileToken: (t: string | null) => void;
  reset: () => void;
}

export function useFileUpload(): UseFileUploadReturn {
  const [state, setState] = useState<UploadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [fileToken, setFileToken] = useState<string | null>(null);

  const reset = useCallback(() => {
    setState("idle");
    setError(null);
    setFileToken(null);
  }, []);

  return { state, error, fileToken, setState, setError, setFileToken, reset };
}
