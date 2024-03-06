import { useFormsQuery } from "@/data/queries";
import { Form } from "@/components/forms/JForm";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { useState } from "react";
import { RJSFSchema } from "@rjsf/utils";

const Element = ({
  className,
  schema,
}: {
  className?: string;
  schema: RJSFSchema;
}) => {
  const [formData, setFormData] = useState(null);
  return (
    <div>
      <Form
        className={className}
        schema={schema}
        formData={formData}
        onChange={(e) => setFormData(e.formData)}
      />
      <br />
      <code className="text-slate-800">
        <pre>{JSON.stringify(formData, null, 2)}</pre>
      </code>
      <br></br>
    </div>
  );
};

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
  return (
    <div>
      <h1 className="text-2xl">Forms</h1>
      <hr></hr>
      <br></br>
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
                      <Element className="my-2" schema={content.Schema} />
                      <CardFooter className="mt-10">
                        <code className="text-slate-800">
                          <pre>{JSON.stringify(content.Schema, null, 2)}</pre>
                        </code>
                        ;
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
