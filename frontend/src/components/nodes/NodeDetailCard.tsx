import { Node } from "@/api/nodeAPI";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function NodeDetailCard({ node }: { node: Node }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{node.Label}  <span className="text-lg text-slate-500">v.{node.Version}</span></CardTitle>
      </CardHeader>
      <CardContent>
        <CardDescription>{node.Description}</CardDescription>
        <Tabs defaultValue="account" className="w-4/5 my-5 text-sm">
          <TabsList>
            <TabsTrigger value="inputs">Inputs</TabsTrigger>
            <TabsTrigger value="options">Options</TabsTrigger>
            <TabsTrigger value="output">Output</TabsTrigger>
          </TabsList>
          <TabsContent value="inputs">Make changes to your account here.</TabsContent>
          <TabsContent value="options">Change your password here.</TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter>
        <p className="text-primary text-sm text-slate-500">{node.Address}</p>
      </CardFooter>
    </Card>
  );
}
