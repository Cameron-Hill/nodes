import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { useFormsQuery } from "@/data/queries";
import { JsonForms } from "@jsonforms/react";
import {
  materialRenderers,
  materialCells,
} from "@jsonforms/material-renderers";

export default function FormsTwo() {
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
                      <JsonForms
                        schema={content.Schema}
                        data={undefined}
                        renderers={materialRenderers}
                        cells={materialCells}
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
