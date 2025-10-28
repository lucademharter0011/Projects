import { DefaultSession } from "next-auth";
import { DefaultJWT } from "next-auth/jwt";

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    accessToken: string;
    refreshToken: string;
    username: string;
    accessTokenExpires: number;
    error?: string;
  }
}

declare module "next-auth" {
  interface Session extends DefaultSession {
    user: {
      id: string;
      name?: string | null;
      username?: string | null;
      email?: string | null;
      accessToken: string;
      refreshToken: string;
    };
    error?: string;
  }

  interface User {
    accessToken: string;
    refreshToken: string;
    accessTokenExpires: number;
    username: string;
  }
}
