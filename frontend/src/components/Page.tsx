import { Outlet } from "react-router-dom";

export default function Page({ children }: { children: React.ReactNode }) {
  return <div className="container mx-auto p-4">
    {children}
    <Outlet />
    </div>;
}
