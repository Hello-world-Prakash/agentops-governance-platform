import NextAuth, { type NextAuthConfig } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import GitHub from "next-auth/providers/github";
import { getRoleFromClaimValues, normalizeRole } from "@/lib/rbac";

function resolveRole(profile: unknown) {
  const profileClaims = profile && typeof profile === "object" ? (profile as Record<string, unknown>) : {};
  return getRoleFromClaimValues([
    profileClaims.role,
    profileClaims.roles,
    profileClaims.groups,
    profileClaims["https://agentops.example.com/roles"],
    process.env.AUTH_DEFAULT_ROLE,
  ]);
}

const providers: NextAuthConfig["providers"] = [];

if (process.env.AUTH_DEMO_LOGIN !== "false") {
  providers.push(
    Credentials({
      name: "Demo SSO",
      credentials: {
        email: { label: "Work email", type: "email", placeholder: "risk.reviewer@example.com" },
        role: { label: "Role", type: "text", placeholder: "Admin" },
      },
      authorize(credentials) {
        const email = typeof credentials?.email === "string" && credentials.email.trim() ? credentials.email.trim() : "demo.admin@agentops.local";
        const role = normalizeRole(credentials?.role ?? process.env.AUTH_DEFAULT_ROLE ?? "Admin");

        return {
          id: email,
          name: email.split("@")[0],
          email,
          role,
        };
      },
    }),
  );
}

if (process.env.AUTH_GITHUB_ID && process.env.AUTH_GITHUB_SECRET) {
  providers.push(
    GitHub({
      clientId: process.env.AUTH_GITHUB_ID,
      clientSecret: process.env.AUTH_GITHUB_SECRET,
    }),
  );
}

export const authConfig = {
  providers,
  secret: process.env.AUTH_SECRET ?? "local-demo-auth-secret-change-before-enabling-sso",
  session: {
    strategy: "jwt",
  },
  trustHost: true,
  callbacks: {
    authorized({ auth }) {
      return Boolean(auth?.user);
    },
    jwt({ token, profile, user }) {
      token.role = user?.role ?? (profile ? resolveRole(profile) : normalizeRole(token.role ?? process.env.AUTH_DEFAULT_ROLE ?? "Admin"));
      return token;
    },
    session({ session, token }) {
      if (session.user && token.sub) {
        session.user.id = token.sub;
        session.user.role = normalizeRole(token.role ?? process.env.AUTH_DEFAULT_ROLE ?? "Admin");
      }
      return session;
    },
  },
} satisfies NextAuthConfig;

export const { auth, handlers, signIn, signOut } = NextAuth(authConfig);
