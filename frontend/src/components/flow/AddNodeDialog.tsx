import { getNodes } from "@/data/api/nodeAPI";
import { Node } from "@/data/api/nodeAPI";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

export function NodeSelectionPanel({
  nodes,
  selected,
  setSelected,
}: {
  nodes: Node[];
  selected: Node | null;
  setSelected: (node: Node | null) => void;
}) {
  const [open, setOpen] = React.useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[300px] justify-between"
        >
          {selected ? selected.Label : "Select a node..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Select a node..." />
          <CommandEmpty>No nodes found.</CommandEmpty>
          <CommandGroup>
            {nodes.map((node) => (
              <CommandItem
                key={node.Address}
                value={node.Address}
                onSelect={(currentValue) => {
                  setSelected(
                    currentValue === selected?.Address.toLowerCase()
                      ? null
                      : nodes.find(
                          (n) =>
                            n.Address.toLowerCase() ===
                            currentValue.toLowerCase(),
                        ) || null,
                  );
                  setOpen(false);
                }}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    selected?.Address.toLowerCase() ===
                      node.Address.toLowerCase()
                      ? "opacity-100"
                      : "opacity-0",
                  )}
                />
                {node.Label}
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export default function AddNodeDialog({
  open,
  setOpen,
  onSubmit,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  onSubmit?: (node: Node) => void;
}) {
  const query = useQuery({ queryFn: getNodes, queryKey: ["nodes"] });
  const [selected, setSelected] = React.useState<Node | null>(null);
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Node</DialogTitle>
          <DialogDescription>
            Please select a node to add to the workflow
          </DialogDescription>
          {query.isLoading && <p>Loading...</p>}
          {query.isError && <p>Error...</p>}
          {query.data && (
            <div className="flex">
              <NodeSelectionPanel
                nodes={query.data}
                selected={selected}
                setSelected={setSelected}
              />
              <Button
                onClick={() => {
                  if (onSubmit && selected) {
                    onSubmit(selected);
                    setOpen(false);
                  } else if (!onSubmit) {
                    console.log(
                      "No onSubmit handler provided to AddNodeDialog.",
                    );
                    setOpen(false);
                  }
                }}
              >
                <Plus />
              </Button>
            </div>
          )}
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
