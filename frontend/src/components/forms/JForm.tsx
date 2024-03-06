import type { RJSFSchema, UiSchema } from "@rjsf/utils";
import type { FormProps as RJSFFormProps } from "@rjsf/core";
import validator from "@rjsf/validator-ajv8";
import RJSFForm from "@rjsf/mui";

export type FormProps = {
  className?: string;
  schema: RJSFSchema;
  formData: RJSFFormProps["formData"];
  onChange: RJSFFormProps["onChange"];
};

const getUISchema = (schemaElement: RJSFSchema): UiSchema => {
  return {};
};

export const Form = ({ className, schema, formData, onChange }: FormProps) => {
  return (
    <RJSFForm
      className={className}
      schema={schema}
      validator={validator}
      formData={formData}
      onChange={onChange}
      uiSchema={getUISchema(schema)}
    />
  );
};
