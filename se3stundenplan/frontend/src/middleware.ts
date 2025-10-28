import { getToken } from "next-auth/jwt";
import { NextRequest, NextResponse } from "next/server";

// Middleware to protect routes and redirect unauthenticated users to the login page
export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  url.pathname = "/login";

  const token = await getToken({ req, secret: process.env.JWT_SECRET });

  const { pathname } = req.nextUrl;

  // If the user is authenticated, allow access to the requested page
  if (pathname.includes("/api/auth") || token) {
    return NextResponse.next();
  }

  // If the user is not authenticated, redirect to the login page
  if (!token && pathname !== url.pathname) {
    return NextResponse.redirect(url);
  }
}

// Export the matcher to apply this middleware to all routes except the login page
export const config = {
  matcher: "/",
};
