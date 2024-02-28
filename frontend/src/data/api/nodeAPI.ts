import { URL } from "../constants";

interface PrimitiveJSONSchema {
  type: "string" | "number" | "boolean" | "null";
  title?: string;
  description?: string;
}

interface ObjectJSONSchema {
  type: "object";
  properties?: {
    [key: string]: JSONSchema;
  };
  additionalProperties?: {
    [key: string]: JSONSchema;
  };
  required?: string[];
  title?: string;
  description?: string;
}

interface ArrayJSONSchema {
  type: "array";
  items: JSONSchema;
}

interface AnyOfJSONSchema {
  anyOf: JSONSchema[];
}

type EmptyObject = Record<string, never>;
type JSONSchema =
  | PrimitiveJSONSchema
  | ObjectJSONSchema
  | ArrayJSONSchema
  | AnyOfJSONSchema
  | EmptyObject;

interface NodeDataItem {
  Type: "input" | "option" | "output";
  Schema: JSONSchema;
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
