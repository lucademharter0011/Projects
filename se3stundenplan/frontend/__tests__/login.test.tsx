import { signIn } from "next-auth/react";
import { useRouter } from "next/router";
import { render, screen, waitFor } from "@testing-library/react";
import Login from "@/pages/login";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";

jest.mock("next-auth/react");
const mockSignIn = signIn as jest.MockedFunction<typeof signIn>;

jest.mock("next/router", () => ({
  useRouter: jest.fn(),
}));
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

jest.mock("next/head", () => {
  return function Head({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
  };
});

jest.mock("next/link", () => {
  return function Link({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) {
    return <a href={href}>{children}</a>;
  };
});

describe("Login Page", () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue({
      push: mockPush,
      pathname: "/login",
      query: {},
      asPath: "/login",
      route: "/login",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any);
  });

  it("renders login form correctly", () => {
    render(<Login />);

    expect(screen.getByText("Bei Ihrem Konto anmelden")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Benutzername oder E-Mail")
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Passwort")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Anmelden" })
    ).toBeInTheDocument();
    expect(screen.getByText("ein neues Konto erstellen")).toBeInTheDocument();
  });

  it("updates form data when user types", async () => {
    const user = userEvent.setup();
    render(<Login />);

    const usernameInput = screen.getByPlaceholderText(
      "Benutzername oder E-Mail"
    );
    const passwordInput = screen.getByPlaceholderText("Passwort");

    await user.type(usernameInput, "testuser");
    await user.type(passwordInput, "testpassword");

    expect(usernameInput).toHaveValue("testuser");
    expect(passwordInput).toHaveValue("testpassword");
  });

  it("toggles password visibility", async () => {
    const user = userEvent.setup();
    render(<Login />);

    const passwordInput = screen.getByPlaceholderText("Passwort");
    const toggleButton = screen.getByRole("button", { name: "" });

    expect(passwordInput).toHaveAttribute("type", "password");

    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute("type", "text");

    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute("type", "password");
  });

  it("handles successful login", async () => {
    const user = userEvent.setup();
    mockSignIn.mockResolvedValue({
      ok: true,
      error: null,
      status: 200,
      url: "/",
    });

    render(<Login />);

    const usernameInput = screen.getByPlaceholderText(
      "Benutzername oder E-Mail"
    );
    const passwordInput = screen.getByPlaceholderText("Passwort");
    const submitButton = screen.getByRole("button", { name: "Anmelden" });

    await user.type(usernameInput, "testuser");
    await user.type(passwordInput, "testpassword");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockSignIn).toHaveBeenCalledWith("credentials", {
        username: "testuser",
        password: "testpassword",
        callbackUrl: "/",
        redirect: false,
      });
      expect(mockPush).toHaveBeenCalledWith("/");
    });
  });

  it("handles login failure with error message", async () => {
    const user = userEvent.setup();
    mockSignIn.mockResolvedValue({
      ok: false,
      error: "CredentialsSignin",
      status: 401,
      url: null,
    });

    render(<Login />);

    const usernameInput = screen.getByPlaceholderText(
      "Benutzername oder E-Mail"
    );
    const passwordInput = screen.getByPlaceholderText("Passwort");
    const submitButton = screen.getByRole("button", { name: "Anmelden" });

    await user.type(usernameInput, "wronguser");
    await user.type(passwordInput, "wrongpassword");
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("Login failed. Please check your credentials.")
      ).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  it("handles unexpected errors", async () => {
    const user = userEvent.setup();
    const consoleSpy = jest.spyOn(console, "error").mockImplementation();

    mockSignIn.mockRejectedValue(new Error("Network error"));

    render(<Login />);

    const usernameInput = screen.getByPlaceholderText(
      "Benutzername oder E-Mail"
    );
    const passwordInput = screen.getByPlaceholderText("Passwort");
    const submitButton = screen.getByRole("button", { name: "Anmelden" });

    await user.type(usernameInput, "testuser");
    await user.type(passwordInput, "testpassword");
    await user.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText("An unexpected error occurred. Please try again.")
      ).toBeInTheDocument();
    });

    expect(consoleSpy).toHaveBeenCalledWith("Login error:", expect.any(Error));
    consoleSpy.mockRestore();
  });

  it("prevents form submission with empty fields", async () => {
    const user = userEvent.setup();
    render(<Login />);

    const submitButton = screen.getByRole("button", { name: "Anmelden" });
    await user.click(submitButton);

    // Validation should prevent submission
    expect(mockSignIn).not.toHaveBeenCalled();
  });
});
