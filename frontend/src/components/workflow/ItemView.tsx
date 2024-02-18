import { Workflow } from "@/api/workflowAPI";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";


export default function ItemView(workflow: Workflow) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{workflow.Name}</CardTitle>
        <CardDescription>Can we have some sort of description here?</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Owner: {workflow.Owner}</p>
      </CardContent>
    </Card>
  );
  
}
