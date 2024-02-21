import Header from "@/components/Header";
import Page from "@/components/Page";
import WorkflowEditorFlow from "@/components/flow/WorkflowEditorFlow";
export default function Flow() {
  return (
    <Page>
      <Header />
      <div className="w-full h-[600px] border">
      <WorkflowEditorFlow workflowID="Workflow-X7aYVSrTfVDutNrFwTSxuB" />
      </div>
    </Page>
  );
}
