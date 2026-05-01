import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Landing from "@/pages/Landing";
import CustomerFunnel from "@/pages/CustomerFunnel";
import TechLogin from "@/pages/TechLogin";
import TechDashboard from "@/pages/TechDashboard";
import AgencyLogin from "@/pages/AgencyLogin";
import AgencyDashboard from "@/pages/AgencyDashboard";

export default function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/try/:slug" element={<CustomerFunnel />} />
          <Route path="/tech/login" element={<TechLogin />} />
          <Route path="/tech/*" element={<TechDashboard />} />
          <Route path="/agency/login" element={<AgencyLogin />} />
          <Route path="/agency/*" element={<AgencyDashboard />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </div>
  );
}
