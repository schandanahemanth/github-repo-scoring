export function AdminPage() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-16">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8">
        <p className="text-sm uppercase tracking-[0.25em] text-brand-100">Admin</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">Control QR inventory and platform actions</h1>
        <p className="mt-4 text-slate-300">
          We&apos;ll use this space for batch QR generation, support review, deactivation, and audit trails.
        </p>
      </div>
    </section>
  );
}
