import { useParams } from "react-router-dom";

export function ScanPage() {
  const { code } = useParams();

  return (
    <section className="mx-auto max-w-3xl px-6 py-16">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8">
        <p className="text-sm uppercase tracking-[0.25em] text-brand-100">Public scan page</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">QR Code: {code}</h1>
        <p className="mt-4 text-slate-300">
          This is the public destination for a scanned QR code. We&apos;ll connect this to the backend public
          QR endpoint next.
        </p>
      </div>
    </section>
  );
}
