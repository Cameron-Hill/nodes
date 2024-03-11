import WorkflowEditorFlow from "@/components/flow/WorkflowEditorFlow";
import { Form } from "@/components/forms/JForm";
import WorkflowSelector from "@/components/workflow/WorkflowSelector";
import { useStore } from "@/store";
import { Fragment, useState } from "react";
import { Navigate, useParams } from "react-router-dom";
import { WorkflowNode } from "@/data/api/workflowAPI";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Separator } from "@radix-ui/react-select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { useSetDataOnNodeMutation } from "@/data/mutations";

const EditNodeField = ({ node }: { node: WorkflowNode }) => {
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [isOpen, setIsOpen] = useState(false);
  const nodeDataMutation = useSetDataOnNodeMutation(
    node.WorkflowID,
    node.NodeID,
  );
  const options = Object.entries(node.Data).filter(
    ([, info]) => info.Type === "options",
  );
  return (
    <Card>
      <CardHeader>{node.Label}</CardHeader>
      <CardContent>
        {options.length > 0 &&
          options.map(([key, info], index) => {
            return (
              <Fragment key={key}>
                {index > 0 && <Separator />}
                {info.Value ? (
                  <div>
                    <b>Value: </b>
                    <span>{JSON.stringify(info.Value)}</span>
                  </div>
                ) : (
                  ""
                )}
                <div>
                  <Form
                    schema={info.Schema}
                    formData={formData[key]}
                    onChange={(e) => {
                      setFormData({ ...formData, [key]: e.formData });
                    }}
                    onSubmit={(e) =>
                      nodeDataMutation.mutate({
                        Key: key,
                        Type: "options",
                        Data: e.formData,
                      })
                    }
                  />
                </div>
              </Fragment>
            );
          })}
      </CardContent>
      <CardFooter>
        <Collapsible
          open={isOpen}
          onOpenChange={setIsOpen}
          className="w-4/5 space-y-2"
        >
          <div className="flex items-center space-x-4 px-4">
            <h4 className="text-sm font-semibold">View Schema</h4>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm">
                <CaretSortIcon className="h-4 w-4" />
                <span className="sr-only">Toggle</span>
              </Button>
            </CollapsibleTrigger>
          </div>
          <CollapsibleContent className="space-y-2">
            <code className="text-slate-800">
              <pre>{JSON.stringify(node, null, 2)}</pre>
            </code>
          </CollapsibleContent>
        </Collapsible>
      </CardFooter>
    </Card>
  );
};

export default function Edit() {
  const { workflowID } = useParams();
  const [selected, setSelected] = useState<string | null>(null);

  if (workflowID && selected) {
    setSelected(null);
  }
  const selectedElements = useStore((state) => state.selected);
  if (selected) {
    return <Navigate to={`/edit/${selected}`} />;
  }
  if (!workflowID) {
    return (
      <WorkflowSelector
        onChange={(workflow) => {
          setSelected(workflow ? workflow.ID : null);
        }}
      />
    );
  }
  return (
    <>
      <div className="h-[600px] w-full border">
        <WorkflowEditorFlow workflowID={workflowID} />
      </div>
      <div className="flex w-full  flex-col">
        {selectedElements.nodes.map((node) => (
          <EditNodeField key={node.id} node={node.data} />
        ))}
      </div>
    </>
  );
}
