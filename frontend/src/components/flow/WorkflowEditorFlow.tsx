import Dagre, { Label } from "@dagrejs/dagre";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import ReactFlow, {
  NodeChange,
  EdgeChange,
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
  applyNodeChanges,
  applyEdgeChanges,
} from "reactflow";
import {
  Edge as EdgeData,
  WorkflowNode as NodeData,
  NodeDataHandle,
  WorkflowDetails,
  addEdgeToWorkflow,
  getWorkflowDetails,
} from "@/data/api/workflowAPI";
import "reactflow/dist/style.css";
import { Button } from "../ui/button";
import WorkflowNode from "./nodes/WorkflowNode";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import EditableEdge from "./edges/EditableEdge";
import AddNodeDialog from "./AddNodeDialog";
import Loader from "../elements/Loader";
import { Save } from "lucide-react";
import ErrorEdge from "./edges/ErrorEdge";
import {
  useMutateSaveWorkflow,
  useWorkflowNodeMutation,
} from "@/data/mutations";
import { useSchedule } from "@/hooks";

const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
const WORKFLOW_NODE_TYPE = "workflow";

const getFlowEdges = (edges: EdgeData[]) => {
  return edges.map((edge) => {
    return {
      id: edge.ID,
      source: edge.From.NodeID,
      target: edge.To.NodeID,
      sourceHandle: edge.From.Key,
      targetHandle: edge.To.Key,
      type: edge.IsSubset ? "editableEdge" : "errorEdge",
      data: edge,
    };
  });
};

const getInitialPosition = (index: number) => {
  return { x: 0, y: 200 * index };
};

const getFlowNodes = (nodes: NodeData[]) => {
  // convert 'our' nodes into react flow nodes
  return nodes.map((node, index) => {
    return {
      id: node.ID,
      position: node.Display ? node.Display : getInitialPosition(index),
      data: node,
      type: WORKFLOW_NODE_TYPE,
    };
  });
};

interface TypedNode extends Node {
  type: string;
}

const getLayoutedElements = (
  nodes: Node[],
  edges: Edge[],
  options: { direction: string },
): { nodes: TypedNode[]; edges: Edge[] } => {
  if (nodes.length === 0) {
    return { nodes: [], edges: [] };
  }
  g.setGraph({ rankdir: options.direction, ranksep: 80 });

  edges.forEach((edge) => g.setEdge(edge.source, edge.target));
  nodes.forEach((node) => g.setNode(node.id, node as Label));

  Dagre.layout(g);

  return {
    nodes: nodes.map((node) => {
      const { x, y } = g.node(node.id);

      return {
        ...node,
        type: node.type ? node.type : WORKFLOW_NODE_TYPE,
        position: { x, y },
      };
    }),
    edges: edges.map((edge) => {
      return {
        ...edge,
        type: edge.type ? edge.type : "editableEdge",
      };
    }),
  };
};

const edgeTypes = {
  editableEdge: EditableEdge,
  errorEdge: ErrorEdge,
};

const nodeTypes = {
  workflow: WorkflowNode,
};

const useAddEdgeMutation = (workflowId: string) => {
  const queryClient = useQueryClient();

  const addEdgeMutation = useMutation({
    mutationFn: (body: { From: NodeDataHandle; To: NodeDataHandle }) =>
      addEdgeToWorkflow(workflowId, body),

    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey: ["workflow", workflowId],
      });
    },
  });

  return addEdgeMutation;
};

const WorkflowPanel = ({
  workflowId,
  nodes,
  edges,
  saving = false,
  setEdges,
  setNodes,
  onSaveRequest,
  onNodesChange,
  onEdgesChange,
  onConnect,
}: {
  workflowId: string;
  nodes: Node[];
  edges: Edge[];
  saving: boolean;
  setEdges: (edges: Edge[]) => void;
  setNodes: (nodes: Node[]) => void;
  onSaveRequest: () => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
}) => {
  const [addingNode, setAddingNode] = useState(false);
  const { fitView } = useReactFlow();
  const addNodeMutation = useWorkflowNodeMutation(workflowId);
  const onLayout = useCallback(
    (direction: string) => {
      const layouted = getLayoutedElements(nodes, edges, { direction });
      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);
      window.requestAnimationFrame(() => {
        fitView();
      });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [nodes, edges],
  );
  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          // onSelectionChange={(elements) => setSelected(elements)}
          fitView
          fitViewOptions={{
            padding: 1,
          }}
        >
          <Panel position="top-left">
            <div className="h-7 w-7">
              {saving && <Loader />}
              {!saving && (
                <Save
                  className="transition-colors hover:text-slate-500"
                  onClick={onSaveRequest}
                />
              )}
            </div>
          </Panel>
          <Panel position="top-right">
            <div className="flex flex-col gap-3">
              <Button
                className="px-2 text-xs"
                variant={"secondary"}
                onClick={() => onLayout("LR")}
              >
                Horizontal Layout
              </Button>
              <Button
                className="px-2 text-xs "
                variant={"secondary"}
                onClick={() => onLayout("TB")}
              >
                Vertical Layout
              </Button>
            </div>
          </Panel>
          <Controls />
          <MiniMap />
          <Background variant={"dots" as BackgroundVariant} gap={12} size={1} />
        </ReactFlow>
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem onClick={() => setAddingNode(true)}>
          Add Node
        </ContextMenuItem>
      </ContextMenuContent>
      <AddNodeDialog
        open={addingNode}
        setOpen={setAddingNode}
        onSubmit={(node) =>
          addNodeMutation.mutate({
            Address: node.Address,
            Version: node.Version,
          })
        }
      ></AddNodeDialog>
    </ContextMenu>
  );
};

const fetchAndSetWorkflowDetails = async (
  workflowID: string,
  setNodes: (nodes: Node[]) => void,
  setEdges: (edges: Edge[]) => void,
  callback?: (data: WorkflowDetails) => void,
) => {
  const workflowDetails = await getWorkflowDetails(workflowID);

  let elements = {
    nodes: getFlowNodes(workflowDetails.nodes),
    edges: getFlowEdges(workflowDetails.edges),
  };

  if (workflowDetails.nodes.every((node) => !node.Display)) {
    console.log("layouting");

    // @ts-expect-error  I don't know why this is happening
    elements = getLayoutedElements(elements.nodes, elements.edges, {
      direction: "TB",
    });
  }

  setNodes(elements.nodes);
  setEdges(elements.edges);
  if (callback) {
    callback(workflowDetails);
  }
  return workflowDetails;
};

//--------------------Main Editor--------------------
export default function WorkflowEditorFlow({
  workflowID,
}: {
  workflowID: string;
}) {
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges] = useEdgesState([]);
  const [saving, setSaving] = useState(false);

  const query = useQuery({
    queryFn: () =>
      fetchAndSetWorkflowDetails(workflowID, setNodes, setEdges, () => {}),

    queryKey: ["workflow", workflowID],
  });

  const saveWorkflowMutation = useMutateSaveWorkflow(workflowID, setSaving);
  const addEdgeMutation = useAddEdgeMutation(workflowID);

  const save = useCallback(() => {
    console.log("Saving");
    saveWorkflowMutation.mutate({ nodes, edges });
  }, [nodes, edges]);

  useSchedule(save, 2000, [edges, nodes]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      return setNodes((nds) => applyNodeChanges(changes, nds));
    },
    [setNodes],
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => applyEdgeChanges(changes, eds));
    },
    [setEdges],
  );
  const onConnect = useCallback(
    (connection: Connection) => {
      const edge = { ...connection, type: "editableEdge" };
      if (
        edge.source === null ||
        edge.target === null ||
        edge.sourceHandle === null ||
        edge.targetHandle === null
      ) {
        console.log("unprocessable edge type: ", edge);
        setEdges((eds: Edge[]) => addEdge(edge, eds));
      } else {
        console.log("Firing Edge mutations");
        addEdgeMutation.mutate({
          From: {
            NodeID: edge.source,
            Key: edge.sourceHandle,
          },
          To: {
            NodeID: edge.target,
            Key: edge.targetHandle,
          },
        });
      }
    },
    [setEdges],
  );
  // eslint-disable-next-line @typescript-eslint/no-unused-vars

  if (query.isError) {
    <div className="flex h-full w-full items-center justify-center">
      <p>Error...</p>
    </div>;
  }

  if (query.isLoading) {
    <div className="flex h-full w-full items-center justify-center">
      <p>Loading...</p>
    </div>;
  }

  if (!query.data) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <p>No Data...</p>
      </div>
    );
  }
  return (
    <div className="h-full w-full">
      <ReactFlowProvider>
        <WorkflowPanel
          workflowId={workflowID}
          setEdges={setEdges}
          setNodes={setNodes}
          saving={saving}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onSaveRequest={() => saveWorkflowMutation.mutate({ nodes, edges })}
          nodes={nodes}
          edges={edges}
        />
      </ReactFlowProvider>
    </div>
  );
}
