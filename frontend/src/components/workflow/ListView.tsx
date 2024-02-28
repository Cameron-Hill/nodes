import { createWorkflow, Workflow } from "@/data/api/workflowAPI";
import {
  Table,
  TableCaption,
  TableBody,
  TableRow,
  TableHead,
  TableHeader,
  TableCell,
} from "@/components/ui/table";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CreateWorkflowDialogButton } from "./CreateWorkflowDialogButton";
import { DeleteWorkflowDialogButton } from "./DeleteCreateWorkflowDialogButton";

const WorkflowListItem = (workflow: Workflow) => {
  return (
    <TableRow key={workflow.ID}>
      <TableCell>✅</TableCell>
      <TableCell>{workflow.Name}</TableCell>
      <TableCell>{workflow.Owner}</TableCell>
    </TableRow>
  );
};

export default function WorkflowListView({
  workflows,
}: {
  workflows: Workflow[];
}) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: createWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
  return (
    <Table>
      <TableCaption className="space-x-32">
        <CreateWorkflowDialogButton
          buttonText="Add"
          onSubmit={mutation.mutate}
        />
        <DeleteWorkflowDialogButton
          buttonText="Delete"
          workflowList={workflows}
        />
      </TableCaption>
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
