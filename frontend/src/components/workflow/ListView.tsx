import { getWorkflows, Workflow } from "@/api/workflowAPI";
import { Table, TableCaption, TableBody, TableRow, TableHead, TableHeader, TableCell } from "@/components/ui/table";
import { useQuery } from "@tanstack/react-query";


const WorkflowListItem = (workflow: Workflow) => {
  return (
    <TableRow key={workflow.ID}>
      <TableCell>✅</TableCell>
      <TableCell>{workflow.Name}</TableCell>
      <TableCell>{workflow.Owner}</TableCell>
      
    </TableRow>
  );
};

export default function WorkflowListView() {
  const query = useQuery({ queryKey: ["workflows"], queryFn: getWorkflows });

  if (query.isLoading) {
    return <div>Loading...</div>;
  }

  if (query.isError) {
    return <div>Error: {query.error.message}</div>;
  }

  let workflows = [] as Workflow[];
  if (query.data) {
    workflows = query.data;
  }

  return (
    <Table>
      <TableCaption>List of available Workflows</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Status</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Owner</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {workflows.map((workflow) => (
          <WorkflowListItem key={workflow.ID} {...workflow} />
        ))}
      </TableBody>
    </Table>
  );
}
