import { useMutateSaveWorkflow } from "@/data/mutations";
import { useCallback } from "react";
import { Node, Edge } from "reactflow";

export default function useAutoSave(
  workflowID: string,
  inProgress: (status: boolean) => void,
  interval: number,
  dependencies: unknown[] = [],
) {
  const useSaveMutation = useMutateSaveWorkflow(workflowID, inProgress);
  const window = Math.floor(new Date().getTime() / (interval * 1000));
  // needs to be a callback inside a callback I think
  const save = useCallback(
    (args: { nodes: Node[]; edges: Edge[] }) => {
      useSaveMutation.mutate(args);
    },
    [window, ...dependencies],
  );
  return save;
}
