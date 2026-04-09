import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl flex-col justify-center px-6 py-16">
      <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="space-y-6">
          <span className="inline-flex rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-1 text-sm text-brand-100">
            QR-based item recovery
          </span>
          <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl">
            Help lost items find their way back to the right owner.
          </h1>
          <p className="max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            FindMyOwner lets people register a secure QR sticker to an item, control what information is
            visible, and receive contact requests from someone who finds it.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/dashboard"
              className="rounded-full bg-brand-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-brand-700"
            >
              Open owner dashboard
            </Link>
            <Link
              to="/q/demo-qr-code"
              className="rounded-full border border-white/15 px-5 py-3 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:text-white"
            >
              View scan page
            </Link>
          </div>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-brand-900/10">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white">Launchable MVP foundation</h2>
            <ul className="space-y-3 text-sm text-slate-300">
              <li>Public scan page with privacy-safe owner and item details</li>
              <li>Owner dashboard to register QR codes and manage lost mode</li>
              <li>Admin tools for QR inventory, reset, and deactivation</li>
              <li>SMS-first identity and contact relay architecture</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
