import { describe, it, expect } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "@/test/test-utils";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { Dialog } from "@/components/ui/Dialog";

describe("UI primitives", () => {
  describe("Button", () => {
    it("renders with primary variant by default", () => {
      renderWithProviders(<Button>Click me</Button>);
      const btn = screen.getByRole("button", { name: /click me/i });
      expect(btn).toBeInTheDocument();
      expect(btn.className).toContain("bg-primary");
    });

    it("renders with different variants", () => {
      renderWithProviders(<Button variant="danger">Delete</Button>);
      const btn = screen.getByRole("button", { name: /delete/i });
      expect(btn.className).toContain("bg-error");
    });
  });

  describe("Input", () => {
    it("renders with label and error", () => {
      renderWithProviders(
        <Input label="Email" error="Email is required" />,
      );
      expect(screen.getByLabelText("Email")).toBeInTheDocument();
      expect(screen.getByText("Email is required")).toBeInTheDocument();
    });
  });

  describe("Card", () => {
    it("renders children", () => {
      renderWithProviders(<Card><p>Card content</p></Card>);
      expect(screen.getByText("Card content")).toBeInTheDocument();
    });

    it("has correct styling classes", () => {
      const { container } = renderWithProviders(
        <Card><p>Content</p></Card>,
      );
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain("rounded-xl");
      expect(card.className).toContain("border-outline-variant");
      expect(card.className).toContain("bg-white");
    });
  });

  describe("Badge", () => {
    it("renders with success variant", () => {
      renderWithProviders(<Badge variant="success">Aprobado</Badge>);
      const badge = screen.getByText("Aprobado");
      expect(badge.className).toContain("bg-green-100");
      expect(badge.className).toContain("text-green-800");
    });

    it("renders with warning variant", () => {
      renderWithProviders(<Badge variant="warning">Pendiente</Badge>);
      const badge = screen.getByText("Pendiente");
      expect(badge.className).toContain("bg-yellow-100");
      expect(badge.className).toContain("text-yellow-800");
    });

    it("renders with error variant", () => {
      renderWithProviders(<Badge variant="error">Error</Badge>);
      const badge = screen.getByText("Error");
      expect(badge.className).toContain("bg-red-100");
      expect(badge.className).toContain("text-red-800");
    });
  });

  describe("Skeleton", () => {
    it("renders with animation class", () => {
      const { container } = renderWithProviders(
        <Skeleton className="h-10 w-64" />,
      );
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain("animate-pulse");
    });
  });

  describe("Dialog", () => {
    it("renders when open", () => {
      renderWithProviders(
        <Dialog open={true} onClose={() => {}} title="Test Dialog">
          <p>Dialog content</p>
        </Dialog>,
      );
      expect(screen.getByText("Test Dialog")).toBeInTheDocument();
      expect(screen.getByText("Dialog content")).toBeInTheDocument();
    });

    it("does not render when closed", () => {
      renderWithProviders(
        <Dialog open={false} onClose={() => {}} title="Hidden Dialog">
          <p>Hidden content</p>
        </Dialog>,
      );
      expect(screen.queryByText("Hidden Dialog")).not.toBeInTheDocument();
    });
  });
});
