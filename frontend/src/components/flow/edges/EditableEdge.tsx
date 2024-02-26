import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import {
  BaseEdge,
  getBezierPath,
  EdgeProps,
  EdgeLabelRenderer,
  useReactFlow,
} from "reactflow";

const EditWidget = ({
  id,
  labelX,
  labelY,
}: {
  id: string;
  labelX: number;
  labelY: number;
}) => {
  const { setEdges } = useReactFlow();
  return (
    <EdgeLabelRenderer>
      <div
        className="m-0 flex justify-center gap-0 overflow-hidden rounded-lg opacity-80"
        style={{
          position: "absolute",
          transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
          pointerEvents: "all",
        }}
      >
        {/* <Button
          className="m-0 h-max w-max rounded-none p-2"
          onClick={() => {
            console.log("edit");
          }}
        >
          <Edit size={7} />
        </Button> */}
        <Button
          variant={"destructive"}
          className="m-0 h-max w-max rounded-none p-2"
          onClick={() => {
            setEdges((es) => es.filter((e) => e.id !== id));
          }}
        >
          <Trash2 size={7} />
        </Button>
      </div>
    </EdgeLabelRenderer>
  );
};

export default function EditableEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  selected,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  });
  // We might want to have Zustand know about the selected element. The we can render a context panel for that element.
  // Let's not bring in Zustand for now.

  return (
    <>
      <BaseEdge id={id} path={edgePath} />
      {selected && <EditWidget id={id} labelX={labelX} labelY={labelY} />}
    </>
  );
}
