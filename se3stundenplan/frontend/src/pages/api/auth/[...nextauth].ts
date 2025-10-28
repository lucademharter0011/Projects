import NextAuth, { AuthOptions, Session } from "next-auth";
import { JWT } from "next-auth/jwt";
import Credentials from "next-auth/providers/credentials";

const refreshAccessToken = async (token: JWT) => {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token.refreshToken}`,
      },
    });

    const data = await res.json();

    if (!res.ok) {
      console.error("Refresh failed:", data);
      throw data;
    }

    return {
      ...token,
      accessToken: data.access_token,
      accessTokenExpires: Date.now() + 24 * 60 * 60 * 1000,
      refreshToken: data.refresh_token ?? token.refreshToken,
      error: undefined,
    };
  } catch (e) {
    console.error("Failed to refresh:", e);
    return { ...token, error: "RefreshAccessTokenError" };
  }
};

export const authOptions: AuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours in seconds
  },
  providers: [
    Credentials({
      name: "Credentials",
      id: "credentials",
      type: "credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        // Attempt to log in with the provided credentials
        try {
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                username: credentials.username,
                password: credentials.password,
              }),
            }
          );

          const data = await res.json();

          if (res.ok && data.user) {
            // Set expiration time for the access token
            const expirationTime = Date.now() + 3600 * 1000;

            return {
              id: data.user.id,
              name: data.user.full_name,
              email: data.user.email,
              username: data.user.username || credentials.username,
              accessToken: data.access_token,
              refreshToken: data.refresh_token,
              accessTokenExpires: expirationTime,
            };
          }

          return null;
        } catch (error) {
          console.error("Login error:", error);
          return null;
        }
      },
    }),
  ],

  callbacks: {
    async jwt({ token, user }): Promise<JWT> {
      // Initial sign in
      if (user) {
        return {
          ...token,
          accessToken: user.accessToken,
          refreshToken: user.refreshToken,
          accessTokenExpires: user.accessTokenExpires,
          username: user.username,
        };
      }

      // Return previous token if the access token has not expired yet
      if (Date.now() < (token.accessTokenExpires as number)) {
        return token;
      }

      return refreshAccessToken(token);
    },

    // Expose token fields to the client via session
    async session({ session, token }): Promise<Session> {
      if (token.error) {
        return {
          ...session,
          error: token.error,
        };
      }

      return {
        ...session,
        user: {
          ...session.user,
          accessToken: token.accessToken,
          refreshToken: token.refreshToken,
          username: token.username,
        },
      };
    },
  },
  pages: {
    signIn: "/login",
  },
};

export default NextAuth(authOptions);
