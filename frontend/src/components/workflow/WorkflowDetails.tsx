import { WorkflowNode, Edge, Workflow, getWorkflowDetails } from "@/api/workflowAPI";
import { useQuery } from "@tanstack/react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "../ui/skeleton";
import { Separator } from "../ui/separator";
import { Button } from "../ui/button";
import { Edit } from "lucide-react";

const DetailsSkeleton = () => {
  return (
    <Skeleton>
      <div>
        <h2>Loading...</h2>
        <sub>Loading...</sub>
      </div>
    </Skeleton>
  );
};

const WorkflowDetailPanel = ({ workflow }: { workflow: Workflow }) => {
  return (
    <div>
      <h2>Workflow</h2>
      <div className="grid gap-4 my-5 ">
        <div className="grid grid-cols-4 items-center gap-4">
          <p>
            <b>Name:</b>
          </p>
          <p>{workflow.Name}</p>
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <p>
            <b>Owner:</b>
          </p>
          <p>{workflow.Owner}</p>
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <p>
            <b>ID:</b>
          </p>
          <p>{workflow.ID}</p>
        </div>
        <Separator />
      </div>
    </div>
  );
};

const NodesDetailPanel = ({ nodes }: { nodes: WorkflowNode[] }) => {
  return (
    <div>
      <h2>Nodes</h2>
      <div className="grid gap-4 my-5">
        {nodes.map((node) => (
          <>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Label:</b>
              </p>
              <p>{node.Label}</p>
            </div>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Version:</b>
              </p>
              <p>{node.Version}</p>
            </div>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>ID:</b>
              </p>
              <p>{node.ID}</p>
            </div>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Address:</b>
              </p>
              <p>{node.Address}</p>
            </div>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Group:</b>
              </p>
              <p>{node.Group}</p>
            </div>
            <div key={node.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>SubGroup:</b>
              </p>
              <p>{node.SubGroup}</p>
            </div>
            <Separator />
          </>
        ))}
      </div>
    </div>
  );
};

const EdgesDetailPanel = ({ edges }: { edges: Edge[] }) => {
  return (
    <div>
      <h2>Edges</h2>
      <div className="grid gap-4 my-5">
        {edges.map((edge) => (
          <>
            <div key={edge.ID} className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Edge ID:</b>
              </p>
              <p>{edge.EdgeID}</p>
            </div>
            <h3>
              <b>From</b>
            </h3>
            <div className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Node ID:</b>
              </p>
              <p>{edge.From.NodeID}</p>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Data Key:</b>
              </p>
              <p>{edge.From.Key}</p>
            </div>
            <h3>
              <b>To</b>
            </h3>
            <div className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Node ID:</b>
              </p>
              <p>{edge.To.NodeID}</p>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <p>
                <b>Data Key:</b>
              </p>
              <p>{edge.To.Key}</p>
            </div>
            <Separator />
          </>
        ))}
      </div>
    </div>
  );
};

export default function WorkflowDetails({ workflow }: { workflow: Workflow }) {
  const query = useQuery({
    queryKey: ["workflow", workflow.ID],
    queryFn: () => getWorkflowDetails(workflow.ID),
  });

  return (
    <Tabs defaultValue="workflow">
      <TabsList>
        <TabsTrigger value="workflow">Workflow</TabsTrigger>
        <TabsTrigger value="nodes">Nodes</TabsTrigger>
        <TabsTrigger value="edges">Edges</TabsTrigger>
      </TabsList>
      <TabsContent value="workflow">
        {query.isLoading && <DetailsSkeleton />}
        {query.isError && <p>Error: {query.error.message}</p>}
        {query.isSuccess && (
          <>
            <WorkflowDetailPanel workflow={query.data.workflow} />
          </>
        )}
      </TabsContent>
      <TabsContent value="nodes">
        {query.isLoading && <DetailsSkeleton />}
        {query.isError && <p>Error: {query.error.message}</p>}
        {query.isSuccess && (
          <>
            <NodesDetailPanel nodes={query.data.nodes} />
            <Button>
              <Edit />
            </Button>
          </>
        )}
      </TabsContent>
      <TabsContent value="edges">
        {query.isLoading && <DetailsSkeleton />}
        {query.isError && <p>Error: {query.error.message}</p>}
        {query.isSuccess && (
          <>
            <EdgesDetailPanel edges={query.data.edges} />
            <Button>
              <Edit />
            </Button>
          </>
        )}
      </TabsContent>
    </Tabs>
  );
}
