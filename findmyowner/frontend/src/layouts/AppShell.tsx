import { Link, Outlet } from "react-router-dom";

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-lg font-semibold tracking-wide text-brand-100">
            FindMyOwner
          </Link>
          <nav className="flex items-center gap-4 text-sm text-slate-300">
            <Link to="/dashboard" className="transition hover:text-white">
              Owner Dashboard
            </Link>
            <Link to="/admin" className="transition hover:text-white">
              Admin
            </Link>
          </nav>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
