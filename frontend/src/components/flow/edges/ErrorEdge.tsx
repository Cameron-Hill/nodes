import EditableEdge, { EdgeProps } from "./EditableEdge";

export default function ErrorEdge(props: EdgeProps) {
  return (
    <>
      <EditableEdge {...props} style={{ stroke: "red" }} />
    </>
  );
}
