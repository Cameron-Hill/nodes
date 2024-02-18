import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./App.css";
import Page from "./components/Page";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import Header from "@/components/Header";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Dev from "@/pages/Dev";

const queryClient = new QueryClient();


const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Page>
        <Header />
      </Page>
    ),
  },
  {
    path: "/dev",
    element: <Dev />,
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
