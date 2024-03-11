import { URL } from "../constants";
import type { RJSFSchema } from "@rjsf/utils";

interface NodeDataItem {
  Type: "input" | "options" | "output";
  Schema: RJSFSchema;
  Value: null | unknown;
}

interface NodeData {
  [key: string]: NodeDataItem;
}

export type Node = {
  Label: string;
  Address: string;
  Group: string | null;
  SubGroup: string | null;
  Version: number;
  Data: NodeData;
  Description: string;
};

export async function getNodes(): Promise<Node[]> {
  const response = await fetch(`${URL}/nodes`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to get nodes");
  }

  return response.json();
}
