import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  deleteEdgeFromWorkflow,
  addNodeToWorkflow,
  batchPutWorkflowEntities,
} from "./api/workflowAPI";

import { Node, Edge } from "reactflow";
import {
  WorkflowNode as NodeData,
  Edge as EdgeData,
} from "@/data/api/workflowAPI";

const getNodeData = (node: Node): NodeData => {
  const nd = node.data;
  nd.Display = node.position;
  return nd;
};

const getEdgeData = (edge: Edge): EdgeData => {
  return edge.data;
};
// Mutations

export const useWorkflowNodeMutation = (workflowId: string) => {
  const queryClient = useQueryClient();

  const addWorkflowNode = useMutation({
    mutationFn: (body: { Address: string; Version: number }) =>
      addNodeToWorkflow(workflowId, body),

    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["workflow", workflowId],
      });
    },
  });

  return addWorkflowNode;
};

export const useMutateSaveWorkflow = (
  workflowId: string,
  inProgress: (status: boolean) => void,
) => {
  const queryClient = useQueryClient();

  const addWorkflowEntities = useMutation({
    mutationFn: ({ nodes, edges }: { nodes: Node[]; edges: Edge[] }) => {
      inProgress(true);
      return batchPutWorkflowEntities(
        workflowId,
        nodes.map((n) => getNodeData(n)),
        edges.map((e) => getEdgeData(e)),
      );
    },

    onSettled: async () => {
      inProgress(false);
      await queryClient.invalidateQueries({
        queryKey: ["workflow", workflowId],
      });
    },
  });

  return addWorkflowEntities;
};

export const useDeleteEdgeMutation = (workflowId: string) => {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (edgeId: string) => deleteEdgeFromWorkflow(workflowId, edgeId),
    onSettled: async () => {
      client.invalidateQueries({ queryKey: ["workflow", workflowId] });
    },
  });
};
