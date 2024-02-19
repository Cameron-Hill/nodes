import Page from "@/components/Page";
import Headers from "@/components/Header";
import WorkflowListView from "@/components/workflow/ListView";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";
import { getWorkflows } from "@/api/workflowAPI";
import { useQuery } from "@tanstack/react-query";

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
  const query = useQuery({ queryFn: getWorkflows, queryKey: ["workflows"] });

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
        {query.isLoading && <p>Loading...</p>}
        {query.isError && <p>Failed to load workflows: {query.error.message}</p>}
        {query.isSuccess && <WorkflowListView workflows={query.data}/>}
      </section>
      <Break className="my-5" />
      <section>
        <h2 className="text-2xl mb-4">Edit Workflow</h2>
        {query.isLoading && <p>Loading...</p>}
        {query.isError && <p>Failed to load workflows: {query.error.message}</p>}
        {query.isSuccess && <WorkflowEditor workflows={query.data} />}
      </section>
      <Break className="my-5" />
      <section>
      <h2 className="text-2xl mb-4">Nodes</h2>  
      {/* I was thinking of putting a data table here. But I think I'm just going to do a select with some sort of Node Display element */}
      <div className="grid grid-cols-2 gap-4">
        <div >
          Hello
        </div>
        <div>
          Hi
        </div>
      </div>

      </section> 
    </Page>
  );
}
