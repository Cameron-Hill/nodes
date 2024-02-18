import { getWorkflow } from "@/api/workflowAPI";
import { useQuery } from "@tanstack/react-query";


export default function ItemView(workflowId: string) {
  const query = useQuery({ queryKey: ["workflows", workflowId], queryFn: ()=> getWorkflow(workflowId) });

  if (query.isLoading) {
    return <div>Loading...</div>;
  }

  if (query.isError) {
    return <div>Error: {query.error.message}</div>;
  }

  let workflow = {} as Workflow;
  if (query.data) {
    workflow = query.data;
  }

  return (
    <div>
      <h1>{workflow.Name}</h1>
      <p>Owner: {workflow.Owner}</p>
      <p>Created: {workflow.Created}</p>
      <p>Modified: {workflow.Modified}</p>
    </div>
  );
  
}
