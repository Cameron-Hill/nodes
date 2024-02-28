import WorkflowSelector from "@/components/workflow/WorkflowSelector";
import { Wrench } from "lucide-react";
import { useState } from "react";
import { Navigate, useParams, Link } from "react-router-dom";

export default function Run() {
  const { workflowID } = useParams();
  const [selected, setSelected] = useState<string | null>(null);
  if (selected) {
    return <Navigate to={`/run/${selected}`} />;
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
    <>
      <h1>💩 This page doesn't exist yet 💩</h1>
      <sub className="text-slate-800">
        You can run your workflows from the{" "}
        <Link
          className="text-blue-700 underline hover:text-blue-400"
          to={`/edit/${workflowID}`}
        >
          edit page
        </Link>
      </sub>
      <div className="mt-5 h-[600px] w-full border">
        {/* <WorkflowEditorFlow workflowID={workflowID} /> */}
        <div className="flex h-full w-full items-center justify-center">
          <Wrench size={75} className="text-slate-400" />
        </div>
      </div>
    </>
  );
}
