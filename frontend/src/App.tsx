import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./App.css";
import Page from "./components/Page";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import Header from "@/components/Header";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Dev from "@/pages/Dev";
import Edit from "./pages/Edit";
import Run from "./pages/Run";
import Forms from "./pages/Forms";
import FormsTwo from "./pages/FormsTwo";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Page>
        <Header />
      </Page>
    ),
    children: [
      {
        path: "dev",
        element: <Dev />,
      },
      {
        path: "edit",
        element: <Edit />,
      },
      {
        path: "edit/:workflowID",
        element: <Edit />,
      },
      {
        path: "run",
        element: <Run />,
      },
      {
        path: "run/:workflowID",
        element: <Run />,
      },
      {
        path: "forms",
        element: <Forms />,
      },
      {
        path: "forms2",
        element: <FormsTwo />,
      },
    ],
  },
]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools initialIsOpen={false} />
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}

export default App;
