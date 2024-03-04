import { Handle, Position, NodeProps } from "reactflow";
import {
  WorkflowNode as NodeData,
  deleteNodeFromWorkflow,
} from "@/data/api/workflowAPI";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ReactNode } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { Trash2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import useLog from "@/hooks/useLog";
import { useStore } from "@/store";

const NodeBody = ({ children }: { children: ReactNode }) => {
  return (
    <div className="min-w-56 rounded-sm bg-neutral-50  px-2 py-4">
      {children}
    </div>
  );
};

const ToolTip = ({
  keyName,
  schema,
  children,
}: {
  keyName: string;
  schema: object;
  children: ReactNode;
}) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent>
          <div className="flex-col gap-2 text-xs">
            <b>{keyName}</b>
            <hr></hr>
            <Collapsible>
              <CollapsibleTrigger>
                <p className="text-blue-400">schema...</p>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <code className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(schema, null, " ")}
                </code>
              </CollapsibleContent>
            </Collapsible>
          </div>
          {/* {JSON.stringify(schema)} */}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const describeSchema = (schema: object) => {};

export default function WorkflowNode({
  id,
  data,
  selected,
  xPos,
  yPos,
}: NodeProps<NodeData>) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const addNodeToSelection = useStore((state) => state.addNodeToSelection);
  const removeNodeFromSelection = useStore(
    (state) => state.removeNodeFromSelection,
  );
  const log = useLog("Node", id, data);

  if (selected) {
    log();
    addNodeToSelection({ id, data, position: { x: xPos, y: yPos } });
  } else {
    removeNodeFromSelection({ id, data, position: { x: xPos, y: yPos } });
  }

  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => deleteNodeFromWorkflow(data.WorkflowID, data.NodeID),
    onSettled: async () => {
      queryClient.invalidateQueries({
        queryKey: ["workflow", data.WorkflowID],
      });
    },
  });

  // const onChange = useCallback((evt: { target: { value: string } }) => {
  //   console.log("change", evt.target.value);
  // }, []);

  const inputs = Object.entries(data.Data).filter(
    ([, value]) => value.Type === "input",
  );
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const options = Object.entries(data.Data).filter(
    ([, value]) => value.Type === "option",
  );
  const outputs = Object.entries(data.Data).filter(
    ([, value]) => value.Type === "output",
  );
  return (
    <>
      {
        //input handles

        inputs.map(([key, value], index) => {
          return (
            <ToolTip key={key} keyName={key} schema={value.Schema}>
              <Handle
                key={key}
                type="target"
                position={Position.Top}
                id={key}
                style={{
                  left: `${((index + 1) * 100) / (inputs.length + 1)}%`,
                }}
              />
            </ToolTip>
          );
        })
      }
      <ContextMenu>
        <ContextMenuTrigger>
          <NodeBody>
            <header className="flex items-center justify-between">
              <h2>{data.Label}</h2>
            </header>
          </NodeBody>
        </ContextMenuTrigger>

        <ContextMenuContent>
          <ContextMenuItem
            onClick={() => mutation.mutate()}
            className="flex gap-3"
          >
            <Trash2 className="text-destructive" />
            <span>Delete Node</span>
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>
      {
        //output handles
        outputs.map(([key, value], index) => {
          return (
            <ToolTip key={key} keyName={key} schema={value.Schema}>
              <Handle
                key={key}
                type="source"
                position={Position.Bottom}
                id={key}
                style={{
                  left: `${((index + 1) * 100) / (outputs.length + 1)}%`,
                }}
              />
            </ToolTip>
          );
        })
      }
    </>
  );
}
