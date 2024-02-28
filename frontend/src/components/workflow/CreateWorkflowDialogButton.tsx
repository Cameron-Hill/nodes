import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Plus } from "lucide-react";
import { WorkflowPost } from "@/data/api/workflowAPI";
import { useState } from "react";

export function CreateWorkflowDialogButton({
  onSubmit,
  buttonText = "Create workflow",
}: {
  buttonText?: string;
  onSubmit?: (body: WorkflowPost) => void;
}) {
  const [body, setBody] = useState<WorkflowPost>({
    Name: "My Workflow",
    Owner: "peduarte",
  });
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus />
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Workflow</DialogTitle>
          <DialogDescription>
            Create a new workflow by filling out the form below.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Workflow Name
            </Label>
            <Input
              id="name"
              value={body.Name}
              className="col-span-3"
              onChange={(e) => {
                setBody({ ...body, Name: e.target.value });
              }}
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="username" className="text-right">
              Owner
            </Label>
            <Input
              id="username"
              value={body.Owner}
              className="col-span-3"
              onChange={(e) => {
                setBody({ ...body, Owner: e.target.value });
              }}
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button
              type="submit"
              onClick={
                onSubmit
                  ? () => {
                      onSubmit(body);
                    }
                  : () => {
                      console.log("No onSubmit function provided");
                    }
              }
            >
              Submit
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
