import "./App.css";
import Page from "./components/Page";
import ReactFlow from "reactflow";

function Header() {
  return (
    <header>
      <h1 className="text-3xl">Nodes</h1>
      <hr />
      <br />
    </header>
  );
}

import "reactflow/dist/style.css";

const initialNodes = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "1" } },
  { id: "2", position: { x: 0, y: 100 }, data: { label: "2" } },
];
const initialEdges = [{ id: "e1-2", source: "1", target: "2" }];

function App() {
  return (
    <>
      <Page>
        <Header />
        <div className="h-dvh bg-gray-800">
          <ReactFlow nodes={initialNodes} edges={initialEdges} />
        </div>
      </Page>
    </>
  );
}

export default App;
