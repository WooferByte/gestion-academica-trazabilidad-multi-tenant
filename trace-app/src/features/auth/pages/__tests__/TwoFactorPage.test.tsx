import { describe, it, expect } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { renderWithProviders } from "@/test/test-utils";
import { TwoFactorPage } from "@/features/auth/pages/TwoFactorPage";
import { AuthProvider } from "@/features/auth/hooks/useAuth";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

function renderTwoFactorPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return renderWithProviders(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TwoFactorPage />
      </AuthProvider>
    </QueryClientProvider>,
    {
      initialEntries: ["/login/2fa"],
    },
  );
}

describe("TwoFactorPage", () => {
  it("renders code input and validates 6 digits", () => {
    renderTwoFactorPage();

    const input = screen.getByLabelText("Código");
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute("maxLength", "6");
    expect(input).toHaveAttribute("inputMode", "numeric");

    expect(
      screen.getByRole("button", { name: /verificar/i }),
    ).toBeInTheDocument();
  });

  it("completes authentication with valid code and redirects to dashboard", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter
          initialEntries={[
            { pathname: "/login/2fa", state: { temp_token: "temp-2fa-token" } },
          ]}
        >
          <Routes>
            <Route
              path="/login/2fa"
              element={
                <AuthProvider>
                  <TwoFactorPage />
                </AuthProvider>
              }
            />
            <Route path="/dashboard" element={<div>Dashboard Page</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    const input = screen.getByLabelText("Código");
    await user.type(input, "123456");
    await user.click(screen.getByRole("button", { name: /verificar/i }));

    await waitFor(() => {
      expect(screen.getByText("Dashboard Page")).toBeInTheDocument();
    });
  });

  it("shows code validation error for non-numeric input", async () => {
    const user = userEvent.setup();
    renderTwoFactorPage();

    const input = screen.getByLabelText("Código");
    await user.type(input, "abc123");

    await user.click(screen.getByRole("button", { name: /verificar/i }));

    await waitFor(() => {
      expect(screen.getByText("Solo números")).toBeInTheDocument();
    });
  });
});
