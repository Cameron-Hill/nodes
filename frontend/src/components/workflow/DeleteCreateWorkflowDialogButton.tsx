import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "../ui/label";
import { Trash2 } from "lucide-react";
import { useState } from "react";
import { Workflow, deleteWorkflow } from "@/data/api/workflowAPI";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DialogClose } from "@radix-ui/react-dialog";

export function DeleteWorkflowPreview({
  workflow,
  onSuccess,
}: {
  workflow: Workflow;
  onSuccess?: () => void;
}) {
  const query = useQuery({
    queryKey: ["deleteWorkflow", workflow.ID, "dryRun"],
    queryFn: () => deleteWorkflow(workflow.ID, true),
  });

  const client = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => deleteWorkflow(workflow.ID),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["workflows"] });
      if (onSuccess) onSuccess();
    },
  });

  if (query.isLoading) {
    return <p>Loading...</p>;
  }
  if (query.isError) {
    return <p>Error: {query.error.message}</p>;
  }
  if (query.data === undefined) {
    return <p>Unable to fetch preview data.</p>;
  }
  const workspaces = query.data.filter((d) => d.Resource === "Workflow");
  const edges = query.data.filter((d) => d.Resource === "Edge");
  const nodes = query.data.filter((d) => d.Resource === "Node");
  return (
    <>
      <div>
        <h2 className="text-sm">
          <b>Workspaces:</b>
        </h2>
        {workspaces.map((w) => (
          <p className="text-xs text-slate-700" key={w.ID}>
            - {w.ID}
          </p>
        ))}
      </div>
      <div>
        <h2 className="text-sm">
          <b>Edges</b>
        </h2>
        {edges.map((e) => (
          <p className="text-xs" key={e.ID}>
            {" "}
            - {e.ID}
          </p>
        ))}
      </div>
      <div>
        <h2 className="text-sm">
          <b>Nodes</b>
        </h2>
        {nodes.map((n) => (
          <p className="text-xs" key={n.ID}>
            {n.ID}
          </p>
        ))}
      </div>
      <DialogClose asChild>
        <AlertDialogAction
          className="bg-destructive"
          onClick={() => {
            mutation.mutate();
          }}
        >
          <Trash2 className="mr-1" />
          Delete
        </AlertDialogAction>
      </DialogClose>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
    </>
  );
}

export function ConfirmDeleteDialog({
  workflow,
  onSuccess,
}: {
  workflow: Workflow | null;
  onSuccess?: () => void;
}) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button disabled={!workflow} variant="destructive">
          <Trash2 className="mr-1" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete the workflow <b>{workflow?.Name}</b>{" "}
            and all of its data.
          </AlertDialogDescription>
        </AlertDialogHeader>

        {workflow && (
          <DeleteWorkflowPreview workflow={workflow} onSuccess={onSuccess} />
        )}
        {!workflow && (
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
          </AlertDialogFooter>
        )}
      </AlertDialogContent>
    </AlertDialog>
  );
}

export function DeleteWorkflowDialogButton({
  workflowList,
  buttonText = "Delete workflow",
  onSuccess,
}: {
  buttonText?: string;
  workflowList: Workflow[];
  onSuccess?: () => void;
}) {
  const [selected, setSelected] = useState<Workflow | null>(null);
  const [submitting, setSubmitting] = useState(false);
  if (submitting && !selected) {
    setSubmitting(false);
  }
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant={"destructive"}>
          <Trash2 className="mr-1" />
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Delete Workflow</DialogTitle>
          <DialogDescription>Delete An Existing Workflow</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="workflowID" className="text-right">
              Workflow
            </Label>
            <Select
              value={selected?.ID}
              onValueChange={(val) => {
                setSelected(workflowList.find((w) => w.ID === val) || null);
              }}
            >
              <SelectTrigger className="w-[280px]">
                <SelectValue placeholder="..." />
              </SelectTrigger>
              <SelectContent>
                {workflowList.map((workflow) => (
                  <SelectItem key={workflow.ID} value={workflow.ID}>
                    {workflow.Name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {selected && (
            <>
              <hr></hr>
              <div className="grid grid-cols-5 items-center gap-2">
                <p>
                  <b>ID:</b>
                </p>
                <p className="text-sm">{selected.ID}</p>
              </div>
              <div className="grid grid-cols-5 items-center gap-2">
                <p>
                  <b>Name:</b>
                </p>
                <p className="text-sm">{selected.Name}</p>
              </div>
              <div className="grid grid-cols-5 items-center gap-2">
                <p>
                  <b>Owner:</b>
                </p>
                <p className="text-sm">{selected.Owner}</p>
              </div>
            </>
          )}
        </div>
        <DialogFooter>
          <ConfirmDeleteDialog
            workflow={selected}
            onSuccess={() => {
              setSelected(null);
              if (onSuccess) onSuccess();
            }}
          />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
