import { getWorkflowDetails } from "@/api/workflowAPI";
import Dagre from "@dagrejs/dagre";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo } from "react";
import ReactFlow, {
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useReactFlow,
  Panel,
  ReactFlowProvider,
} from "reactflow";
import { Edge as EdgeData, WorkflowNode as NodeData } from "@/api/workflowAPI";
import "reactflow/dist/style.css";
import { Button } from "../ui/button";

// const initialNodes = [
//   { id: "1", position: { x: 0, y: 0 }, data: { label: "1" } },
//   { id: "2", position: { x: 0, y: 100 }, data: { label: "2" } },
// ];
// const initialEdges = [{ id: "e1-2", source: "1", target: "2" }];

const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

const getFlowEdges = (edges: EdgeData[]) => {
  return edges.map((edge) => {
    return {
      id: edge.ID,
      source: edge.From.NodeID,
      target: edge.To.NodeID,
      sourceHandle: edge.From.Key,
      targetHandle: edge.To.Key,
    };
  });
};

const getInitialPosition = (index: number) => {
  return { x: 0, y: 200 * index };
};

const getFlowNodes = (nodes: NodeData[]) => {
  return nodes.map((node, index) => {
    return {
      id: node.ID,
      position: getInitialPosition(index),
      data: { label: node.Label },
    };
  });
};

const getLayoutedElements = (nodes: Node[], edges: Edge[], options: { direction: string }) => {
  g.setGraph({ rankdir: options.direction,  ranksep: 80});

  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  nodes.forEach((node) => g.setNode(node.id, node));

  Dagre.layout(g);

  return {
    nodes: nodes.map((node) => {
      const { x, y } = g.node(node.id);

      return { ...node, position: { x, y } };
    }),
    edges,
  };
};

const WorkflowPanel = (props: { nodes: Node[]; edges: Edge[] }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(props.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(props.edges);
  const { fitView } = useReactFlow();
  useMemo(() => {
    
    console.log("fitView" )
  }, [])

  console.log(nodes);
  const onConnect = useCallback((params: Edge | Connection) => {
    setEdges((eds) => addEdge(params, eds))
  }, [setEdges]);
  const onLayout = useCallback(
    (direction: string) => {
      const layouted = getLayoutedElements(nodes, edges, { direction });
      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);
      window.requestAnimationFrame(() => {
        fitView();
      });
    },
    [nodes, edges]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
      fitViewOptions={{
        padding: 1
      }}
    >
      <Panel position="top-right">
        <div className="flex flex-col gap-3">
        <Button className="text-xs px-2" variant={"secondary"} onClick={() => onLayout("LR")}>Horizontal Layout</Button>
        <Button className="text-xs px-2" variant={"secondary"} onClick={() => onLayout("TB")}>Vertical Layout</Button>
        </div>
      </Panel>
      <Controls />
      <MiniMap />
      <Background variant={"dots" as BackgroundVariant} gap={12} size={1} />
    </ReactFlow>
  );
};

export default function WorkflowEditorFlow({ workflowID }: { workflowID: string }) {
  const query = useQuery({ queryFn: () => getWorkflowDetails(workflowID), queryKey: ["workflow", workflowID] });
  // eslint-disable-next-line @typescript-eslint/no-unused-vars

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

  if (!query.data) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <p>No Data...</p>
      </div>
    );
  }

  const elements = getLayoutedElements(getFlowNodes(query.data.nodes), getFlowEdges(query.data.edges), {
    direction: "TB",
  });

  console.log(query.data);
  return (
    <div className="w-full h-full">
      <ReactFlowProvider>
        <WorkflowPanel {...elements} />
      </ReactFlowProvider>
    </div>
  );
}
