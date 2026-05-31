import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  // Barcha yo'llar, lekin api/_next/static/media bundan mustasno
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
