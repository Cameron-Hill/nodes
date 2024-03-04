import { useFormsQuery } from "@/data/queries";

import { RJSFSchema } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
// import Form from "@rjsf/core";
// import Form from "@rjsf/bootstrap-4";
import Form from "@rjsf/mui";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { JsonSchemaProperty } from "@/types";

const schema: RJSFSchema = {
  title: "Test form",
  type: "string",
};

function getStringUISchema() {
  return {
    "ui:widget": "textarea",
  };
}

function getNumberUISchema() {
  return {
    "ui:widget": "updown",
  };
}

function getUISchema(property: JsonSchemaProperty) {
  switch (property.type) {
    case "string":
      return getStringUISchema();
    case "number":
      return getNumberUISchema();
    case "boolean":
      return {};
    default:
      return {};
  }
}

export default function Forms() {
  const query = useFormsQuery();
  if (query.isLoading) {
    return <div>Loading...</div>;
  }
  if (query.isError) {
    return <div>Error: {query.error.message}</div>;
  }
  if (!query.data) {
    return <div>No data</div>;
  }
  console.log(query.data);
  return (
    <div>
      <h1 className="text-2xl">Forms</h1>
      <hr></hr>
      <br />
      <Form schema={schema} validator={validator} />
      <br />
      <hr></hr>
      <br />
      {Object.entries(query.data).map(([key, data]) => {
        return (
          <div key={key}>
            <br></br>
            <h2 className="text-xl" key={key}>
              {data.Label}
            </h2>
            <sub>{data.Address}</sub>
            <p>{data.Description}</p>
            {data.Data &&
              Object.entries(data.Data).map(([name, content]) => {
                return (
                  <Card className="m-3" key={name}>
                    <CardHeader>
                      <h3 className="text-lg ">{name}</h3>
                    </CardHeader>
                    <CardContent>
                      <p>
                        <b>Type:</b> {content.Type}
                      </p>
                      <p>
                        <b>Value:</b> {JSON.stringify(content.Value)}
                      </p>
                      <Form
                        className="my-2"
                        schema={content.Schema}
                        validator={validator}
                      />
                      <CardFooter className="mt-10">
                        {JSON.stringify(content.Schema)}
                      </CardFooter>
                    </CardContent>
                  </Card>
                );
              })}
            <br></br>
            <hr></hr>
          </div>
        );
      })}
    </div>
  );
}
