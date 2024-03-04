export interface JsonSchema {
  title: string;
  description: string;
  properties: JsonSchemaProperties;
}

export interface JsonSchemaProperties {
  [key: string]: JsonSchemaProperty;
}

export interface JsonSchemaProperty {
  type: string;
  description: string;
}
