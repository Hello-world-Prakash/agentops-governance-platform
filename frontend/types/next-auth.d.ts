import "next-auth";
import "next-auth/jwt";
import type { Role } from "@/lib/rbac";

declare module "next-auth" {
  interface User {
    id?: string;
    role?: Role;
  }

  interface Session {
    user?: {
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: Role;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    role?: Role;
  }
}
