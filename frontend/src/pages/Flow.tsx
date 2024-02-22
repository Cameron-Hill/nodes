import { getWorkflows } from "@/api/workflowAPI";
import WorkflowEditorFlow from "@/components/flow/WorkflowEditorFlow";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";
import { useQuery } from "@tanstack/react-query";
import { redirect, useParams } from "react-router-dom";

const WorkflowSelector = () => {
  const query = useQuery({ queryFn: getWorkflows, queryKey: ["workflows"] });
  if (query.isLoading) {
    return <p>Loading...</p>;
  }
  if (query.isError) {
    return <p>Error: {query.error.message}</p>;
  }
  if (!query.data) {
    return <p>No data</p>;
  }
  return (
    <WorkflowEditor
      workflows={query.data}
      onChange={(workflow) => {
        if (workflow) {
          redirect(`/flow/${workflow.ID}`);
        }
      }}
    />
  );
};

export default function Flow() {
  const { workflowID } = useParams();

  if (!workflowID) {
    return <WorkflowSelector />;
  }
  return (
    <div className="w-full h-[600px] border">
      <WorkflowEditorFlow workflowID={workflowID} />
    </div>
  );
}
