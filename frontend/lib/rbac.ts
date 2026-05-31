export const ROLES = ["Admin", "Claims Adjuster", "Risk Reviewer", "Auditor", "Read-only Viewer"] as const;

export type Role = (typeof ROLES)[number];

export type Permission =
  | "dashboard:view"
  | "claims:submit"
  | "claims:review"
  | "highRisk:approve"
  | "audit:view"
  | "policies:manage"
  | "users:manage"
  | "agents:manage";

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  Admin: ["dashboard:view", "claims:submit", "claims:review", "highRisk:approve", "audit:view", "policies:manage", "users:manage", "agents:manage"],
  "Claims Adjuster": ["dashboard:view", "claims:submit", "claims:review"],
  "Risk Reviewer": ["dashboard:view", "claims:review", "highRisk:approve", "audit:view"],
  Auditor: ["dashboard:view", "audit:view"],
  "Read-only Viewer": ["dashboard:view"],
};

export const ROLE_DESCRIPTIONS: Record<Role, string> = {
  Admin: "Manage policies, users, agents, claims, approvals, and audit visibility.",
  "Claims Adjuster": "Submit and review claims without high-risk approval authority.",
  "Risk Reviewer": "Approve or reject high-risk decisions and inspect risk evidence.",
  Auditor: "View audit logs and governance evidence only.",
  "Read-only Viewer": "View dashboard posture without workflow actions.",
};

export function normalizeRole(value: unknown): Role {
  if (typeof value !== "string") {
    return "Read-only Viewer";
  }

  const normalized = value.trim().toLowerCase().replaceAll("_", " ").replaceAll("-", " ");
  const match = ROLES.find((role) => role.toLowerCase() === normalized);
  return match ?? "Read-only Viewer";
}

export function hasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role].includes(permission);
}

export function getRoleFromClaimValues(values: unknown[]): Role {
  for (const value of values) {
    if (typeof value === "string") {
      const role = normalizeRole(value);
      if (role !== "Read-only Viewer" || value.toLowerCase().includes("viewer")) {
        return role;
      }
    }

    if (Array.isArray(value)) {
      const nestedRole = getRoleFromClaimValues(value);
      if (nestedRole !== "Read-only Viewer") {
        return nestedRole;
      }
    }
  }

  return "Read-only Viewer";
}

