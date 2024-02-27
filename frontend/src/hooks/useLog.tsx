import { useCallback } from "react";

export default function useLog(...args: unknown[]) {
  return useCallback(() => console.log(...args), [args]);
}
