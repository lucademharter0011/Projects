import AppHeader from "./app-header";

export default function AppLayout({ children }: React.PropsWithChildren) {
  return (
    <div className="mx-auto px-4 container relative">
      <AppHeader />
      {children}
    </div>
  );
}
