import Page from "@/components/Page";
import Headers from "@/components/Header";
import WorkflowListView from "@/components/workflow/ListView";

const Break = () => {
  return (
    <>
      <br />
      <br />
      <hr />
      <br />
      <br />
    </>
  );
};

export default function Dev() {
  return (
    <Page>
      <Headers />
      <section className="mt-4">
        <h1 className="text-3xl pb-3">Dev Tools</h1>
        <p>This is a page for development purposes. It is not meant to be part of the final product.</p>
      </section>
      <Break />
      <section>
        <WorkflowListView />
      </section>
    <Break />
    </Page>
  );
}
