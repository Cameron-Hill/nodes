const URL = 'http://localhost:8081'

export type APIError = {
  detail: string;
};

export type Workflow = {
  WorkflowId: string;
  Name: string;
  Owner: string;
  ID: string;
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