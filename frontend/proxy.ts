import { auth } from "@/auth";

const authRequired = process.env.NEXT_PUBLIC_AUTH_REQUIRED !== "false";

export default auth((request) => {
  if (!authRequired) {
    return;
  }

  const isAuthenticated = Boolean(request.auth?.user);
  const isAuthRoute = request.nextUrl.pathname.startsWith("/api/auth");

  if (!isAuthenticated && !isAuthRoute) {
    const signInUrl = new URL("/api/auth/signin", request.nextUrl.origin);
    signInUrl.searchParams.set("callbackUrl", request.nextUrl.href);
    return Response.redirect(signInUrl);
  }
});

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
