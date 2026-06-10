import { describe, it } from "vitest";
import { renderWithProviders } from "@/test/test-utils";
import { AuthProvider } from "@/features/auth/hooks/useAuth";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("Full auth flow", () => {
  it("initializes auth provider", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <div>App initialized</div>
        </AuthProvider>
      </QueryClientProvider>,
      { initialEntries: ["/"] },
    );
  });
});
