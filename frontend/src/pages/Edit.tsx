import WorkflowEditorFlow from "@/components/flow/WorkflowEditorFlow";
import WorkflowSelector from "@/components/workflow/WorkflowSelector";
import { useState } from "react";
import { Navigate, useParams } from "react-router-dom";

export default function Edit() {
  const { workflowID } = useParams();
  const [selected, setSelected] = useState<string | null>(null);
  if (selected) {
    return <Navigate to={`/edit/${selected}`} />;
  }
  if (!workflowID) {
    return (
      <WorkflowSelector
        onChange={(workflow) => {
          setSelected(workflow ? workflow.ID : null);
        }}
      />
    );
  }
  return (
    <div className="h-[600px] w-full border">
      <WorkflowEditorFlow workflowID={workflowID} />
    </div>
  );
}
