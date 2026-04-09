import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { AdminPage } from "../pages/AdminPage";
import { HomePage } from "../pages/HomePage";
import { OwnerDashboardPage } from "../pages/OwnerDashboardPage";
import { ScanPage } from "../pages/ScanPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/q/:code" element={<ScanPage />} />
        <Route path="/dashboard" element={<OwnerDashboardPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
