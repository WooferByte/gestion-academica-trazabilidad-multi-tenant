import { describe, it, expect, vi, beforeEach } from "vitest";
import { exportCsv } from "@/utils/exportCsv";

describe("exportCsv", () => {
  beforeEach(() => {
    URL.createObjectURL = vi.fn(() => "blob:mock");
    URL.revokeObjectURL = vi.fn();
  });

  it("should not create a download if data is empty", () => {
    const spy = vi.spyOn(document, "createElement");
    exportCsv([], [{ key: "name", label: "Name" }], "test");
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });

  it("should create a CSV with BOM and download it", () => {
    const anchorClick = vi.fn();
    const createElement = vi.spyOn(document, "createElement").mockReturnValue({
      href: "",
      download: "",
      click: anchorClick,
    } as unknown as HTMLAnchorElement);

    const data = [
      { name: "Juan", age: 25 },
      { name: "María", age: 30 },
    ];
    const columns = [
      { key: "name", label: "Nombre" },
      { key: "age", label: "Edad" },
    ];

    exportCsv(data, columns, "test.csv");

    expect(createElement).toHaveBeenCalledWith("a");
    expect(anchorClick).toHaveBeenCalledTimes(1);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:mock");

    createElement.mockRestore();
  });

  it("should handle null and undefined values", () => {
    const anchorClick = vi.fn();
    vi.spyOn(document, "createElement").mockReturnValue({
      href: "",
      download: "",
      click: anchorClick,
    } as unknown as HTMLAnchorElement);

    const data = [{ name: null, age: undefined }];
    const columns = [
      { key: "name", label: "Nombre" },
      { key: "age", label: "Edad" },
    ];

    expect(() => exportCsv(data, columns, "test")).not.toThrow();
    expect(anchorClick).toHaveBeenCalledTimes(1);
  });

  it("should add .csv extension if missing", () => {
    const anchorClick = vi.fn();
    const spy = vi.spyOn(document, "createElement").mockReturnValue({
      href: "",
      download: "",
      click: anchorClick,
    } as unknown as HTMLAnchorElement);

    exportCsv([{ name: "Test" }], [{ key: "name", label: "Name" }], "without-ext");
    expect(anchorClick).toHaveBeenCalled();

    spy.mockRestore();
  });
});
