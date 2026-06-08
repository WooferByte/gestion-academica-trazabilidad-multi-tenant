import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@/providers/RouterProvider";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider />
    </QueryClientProvider>
  );
}

export default App;
