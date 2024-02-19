import { Workflow } from "@/api/workflowAPI";
import { useState } from "react";
import { Button } from "../ui/button";
import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import WorkflowDetails from "./WorkflowDetails";

export default function WorkflowEditor({ workflows }: { workflows: Workflow[] }) {
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState("");
  const workflow = workflows.find((workflow) => workflow.ID === value);

  return (
    <div className="flex flex-col gap-5">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-[400px] justify-between overflow-clip"
          >
            {value ? workflows.find((workflow) => workflow.ID === value)?.Name : "Select workflow..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[400px] p-0">
          <Command>
            <CommandInput placeholder="Search Workflows..." />
            <CommandEmpty>No workflow found.</CommandEmpty>
            <CommandGroup className="whitespace-nowrap">
              {workflows.map((workflow) => (
                <CommandItem
                  key={workflow.ID}
                  value={workflow.ID}
                  onSelect={(currentValue) => {
                    setValue(currentValue === value ? "" : workflow.ID);
                    setOpen(false);
                  }}
                >
                  <Check className={cn("mr-2 h-4 w-4", value === workflow.ID ? "opacity-100" : "opacity-0")} />
                  {workflow.Name}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>

      {workflow && <WorkflowDetails workflow={workflow} />}

      
    </div>
  );
}
