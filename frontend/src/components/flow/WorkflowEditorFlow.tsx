import { getWorkflowDetails } from "@/api/workflowAPI";
import { useQuery } from "@tanstack/react-query";
import { useCallback } from "react";
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
} from "reactflow";

import "reactflow/dist/style.css";

const initialNodes = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "1" } },
  { id: "2", position: { x: 0, y: 100 }, data: { label: "2" } },
];
const initialEdges = [{ id: "e1-2", source: "1", target: "2" }];

export default function WorkflowEditorFlow({ workflowID }: { workflowID: string }) {

  
  const query = useQuery({ queryFn: () => getWorkflowDetails(workflowID), queryKey: ["workflow", workflowID] });
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  if (query.isSuccess) {
    console.log(query.data);
  }

  if (query.isError) {
    <div className="w-full h-full flex items-center justify-center">
      <p>Error...</p>
    </div>;
  }

  if (query.isLoading) {
    <div className="w-full h-full flex items-center justify-center">
      <p>Loading...</p>
    </div>;
  }

  const onConnect = useCallback((params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
    >
      <Controls />
      <MiniMap />
      <Background variant={"dots" as BackgroundVariant} gap={12} size={1} />
    </ReactFlow>
  );
}
