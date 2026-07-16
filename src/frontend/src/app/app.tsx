import { ErrorBoundary } from "@/app/error-boundary";
import { RoutingPage } from "@/features/routing/components/routing-page";

export function App() {
  return (
    <ErrorBoundary fallback={<main className="app-error">The application could not be loaded. Please refresh the page.</main>}>
      <RoutingPage />
    </ErrorBoundary>
  );
}
