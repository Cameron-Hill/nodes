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
import { Workflow, deleteWorkflow } from "@/api/workflowAPI";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
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
import { useQuery } from "@tanstack/react-query";

export function DeleteWorkflowPreview({
  workflow,
}: {
  workflow: Workflow;
  onPreviewReady: (ready: boolean) => void;
}) {
  const query = useQuery({
    queryKey: ["deleteWorkflow", workflow.ID, "dryRun"],
    queryFn: () => deleteWorkflow(workflow.ID, true),
  });
  console.log("Preview Fired!");

  if (query.isLoading) {
    return <p>Loading...</p>;
  }
  if (query.isError) {
    return <p>Error: {query.error.message}</p>;
  }
  if (query.data === undefined) {
    return <p>Unable to fetch preview data.</p>;
  }
  return (
    <div>
      {query.data.map((item) => (
        <div key={item.ID} className="grid grid-cols-5 items-center gap-2"></div>
      ))}
    </div>
  );
}

export function ConfirmDeleteDialog({ workflow }: { workflow: Workflow | null }) {
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
            This will permanently delete the workflow <b>{workflow?.Name}</b> and all of its data.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogContent>
          {workflow && <DeleteWorkflowPreview workflow={workflow} />}
        </AlertDialogContent>
        {!workflow && (
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-destructive">
              <Trash2 className="mr-1" />
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        )}
      </AlertDialogContent>
    </AlertDialog>
  );
}

export function DeleteWorkflowDialogButton({
  workflowList,
  buttonText = "Delete workflow",
}: {
  buttonText?: string;
  workflowList: Workflow[];
}) {
  const [selected, setSelected] = useState<Workflow | null>(null);
  const [submitting, setSubmitting] = useState(false);
  if (submitting && !selected) {
    setSubmitting(false);
  }
  console.log("submitting", submitting, "selected", selected);
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
          <ConfirmDeleteDialog workflow={selected} />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
