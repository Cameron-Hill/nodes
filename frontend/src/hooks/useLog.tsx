import { useCallback } from "react";

export default function useLog(...args: unknown[]) {
  return useCallback(() => {
    if (false) {
      console.log(...args);
    }
  }, [args]);
}
