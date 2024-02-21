const URL = "http://localhost:8081";

export type APIError = {
  detail: string;
};

export type Workflow = {
  WorkflowId: string;
  Name: string;
  Owner: string;
  ID: string;
  Resource: "Workflow"
};

interface NodeDataItem {
  Type: "input" | "option" | "output";
  Schema: object;
  Value: unknown;
}
interface NodeData {
  [key: string]: NodeDataItem;
}

interface NodeDataHandle {
  NodeID: string;
  Key: string;
}

export type Node = {
  Label: string;
  Address: string;
  Group: string | null;
  SubGroup: string | null;
  Version: number;
  Data: NodeData;
  WorkflowID: string;
  NodeID: string;
  ID: string;
  Resource: "Node";
};

export type Edge = {
  WorkflowID: string;
  EdgeID: string;
  ID: string;
  From: NodeDataHandle;
  To: NodeDataHandle;
  Resource: "Edge";
};
export type WorkflowPost = {
  Name: string;
  Owner: string;
};

export type WorkflowDetails = {
  workflow: Workflow;
  nodes: Node[];
  edges: Edge[];
};

export async function getWorkflows(): Promise<Workflow[]> {
  const response = await fetch(`${URL}/workflows/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}

export async function getWorkflow(workflowId: string): Promise<Workflow> {
  const response = await fetch(`${URL}/workflows/${workflowId}/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}

export async function createWorkflow(body: WorkflowPost): Promise<Workflow> {
  const response = await fetch(`${URL}/workflows/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}

export async function deleteWorkflow(workflowId: string, dryRun: boolean = false): Promise<(Workflow | Edge | Node)[]> {
  const response = await fetch(`${URL}/workflows/${workflowId}?` + new URLSearchParams({ dryRun: dryRun.toString() }), {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}


export async function getWorkflowDetails(workflowId: string): Promise<WorkflowDetails> {
  const response = await fetch(`${URL}/workflows/${workflowId}/all`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  const workflow = data.find((d: { Resource: string; }) => d.Resource === "Workflow");
  const edges = data.filter((d: { Resource: string; }) => d.Resource === "Edge");
  const nodes = data.filter((d: { Resource: string; }) => d.Resource === "Node");
  return { workflow, nodes, edges};  
}


export async function getNodes(){
  const response = await fetch(`${URL}/nodes/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}