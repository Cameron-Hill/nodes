import Page from "@/components/Page";
import Headers from "@/components/Header";
import WorkflowListView from "@/components/workflow/ListView";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";
import { getWorkflows } from "@/api/workflowAPI";
import {getNodes, Node} from "@/api/nodeAPI";
import { useQuery } from "@tanstack/react-query";
import NodeTableSelector from "@/components/nodes/NodeTableSelector";
import { useState } from "react";
import NodeDetailCard from "@/components/nodes/NodeDetailCard";

const Break = ({ className = "" }: { className: string }) => {
  return (
    <div className={className}>
      <br />
      <br />
      <hr />
      <br />
      <br />
    </div>
  );
};

export default function Dev() {
  const workflowsQuery = useQuery({ queryFn: getWorkflows, queryKey: ["workflows"] });
  const nodesQuery = useQuery({ queryFn: getNodes, queryKey: ["nodes"] });
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  return (
    <Page>
      <Headers />
      <section className="mt-4">
        <h1 className="text-3xl pb-3">Dev Tools</h1>
        <p>This is a page for development purposes. It is not meant to be part of the final product.</p>
      </section>
      <Break className="my-5" />
      <section>
        <h2 className="text-2xl">Workflows</h2>
        {workflowsQuery.isLoading && <p>Loading...</p>}
        {workflowsQuery.isError && <p>Failed to load workflows: {workflowsQuery.error.message}</p>}
        {workflowsQuery.isSuccess && <WorkflowListView workflows={workflowsQuery.data}/>}
      </section>
      <Break className="my-5" />
      <section>
        <h2 className="text-2xl mb-4">Edit Workflow</h2>
        {workflowsQuery.isLoading && <p>Loading...</p>}
        {workflowsQuery.isError && <p>Failed to load workflows: {workflowsQuery.error.message}</p>}
        {workflowsQuery.isSuccess && <WorkflowEditor workflows={workflowsQuery.data} />}
      </section>
      <Break className="my-5" />
      <section>
      <h2 className="text-2xl mb-4">Nodes</h2>  
      {/* I was thinking of putting a data table here. But I think I'm just going to do a select with some sort of Node Display element */}
      <div className="grid grid-cols-2 gap-8">
        <div >
        {nodesQuery.isLoading && <p>Loading...</p>}
        {nodesQuery.isError && <p>Failed to load nodes: {nodesQuery.error.message}</p>}
        {nodesQuery.isSuccess && <NodeTableSelector nodes={nodesQuery.data} setSelected={setSelectedNode} selected={selectedNode}/>}
        </div>
        <div>
        {!selectedNode && <><p className=" my-3 text-primary w-full text-center ">Select a node to see details</p> <hr></hr></>}
        {selectedNode && <NodeDetailCard node={selectedNode}/>}
        
        </div>
      </div>

      </section> 
    </Page>
  );
}
