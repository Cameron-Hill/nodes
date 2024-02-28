import { useQuery } from "@tanstack/react-query";
import { getWorkflow, getWorkflows } from "@/data/api/workflowAPI";

export const useWorkflowsQuery = () => {
  return useQuery({
    queryFn: getWorkflows,
    queryKey: ["workflows"],
  });
};
export const useWorkflowQuery = (workflowID: string) => {
  return useQuery({
    queryFn: () => getWorkflow(workflowID),
    queryKey: ["workflow", workflowID],
  });
};
