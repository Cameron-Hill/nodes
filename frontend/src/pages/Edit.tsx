import WorkflowEditorFlow from "@/components/flow/WorkflowEditorFlow";
import WorkflowSelector from "@/components/workflow/WorkflowSelector";
import { useStore } from "@/store";
import { useState } from "react";
import { Navigate, useParams } from "react-router-dom";

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
        {selectedElements.nodes.map((node) => {
          console.log(node);
          return (
            <div>
              <h1>{node.data.Label}</h1>
              {Object.entries(node.data.Data).map(([key, value]) => {
                return (
                  <div>
                    <h2>{key}</h2>
                    <sub>{value.Type}</sub>
                    <p>---------------------</p>
                    <p>{value.Value ? JSON.stringify(value.Value) : "unset"}</p>
                    <br></br>
                    {/* <Form
                      schema={value.Schema}
                      validator={validator}
                      onChange={() => console.log("changed")}
                      onSubmit={() => console.log("submitted")}
                      onError={() => console.log("errors")}
                    /> */}
                  </div>
                );
              })}
            </div>
          );
        })}
        {selectedElements.edges.map((edge) => {
          console.log(edge);
          return (
            <>
              <h1>{edge.data.Label}</h1>
              {/* <Form
                schema={schema}
                validator={validator}
                onChange={log("changed")}
                onSubmit={log("submitted")}
                onError={log("errors")}
              /> */}
            </>
          );
        })}
      </div>
    </>
  );
}
