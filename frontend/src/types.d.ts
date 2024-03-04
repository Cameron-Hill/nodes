export interface JSONSchema {
  title: string;
  description: string;
  properties: JSONSchemaProperties;
}

export interface JSONSchemaProperties {
  [key: string]: JsonSchemaProperty;
}

export type JSONSchemaProperty =
  | AnyOfJSONSchemaProperty
  | PrimitiveJSONSchemaProperty
  | ObjectJSONSchemaProperty
  | ArrayJSONSchemaProperty
  | EmptyObject;

interface PrimitiveJSONSchemaProperty {
  type: "string" | "number" | "boolean" | "null";
  title?: string;
  description?: string;
}
interface ObjectJSONSchemaProperty {
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

interface ArrayJSONSchemaProperty {
  type: "array";
  items: JSONSchema;
}

interface AnyOfJSONSchemaProperty {
  anyOf: JSONSchema[];
}

type EmptyObject = Record<string, never>;
