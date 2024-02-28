import { useWorkflowsQuery } from "@/data/queries";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";
import { Workflow } from "@/data/api/workflowAPI";

export default function WorkflowSelector({
  onChange,
}: {
  onChange: (workflow: Workflow | null) => void;
}) {
  const query = useWorkflowsQuery();
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
      onChange={(workflow) => onChange(workflow)}
    />
  );
}
