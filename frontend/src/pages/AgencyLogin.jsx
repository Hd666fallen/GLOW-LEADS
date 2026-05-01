import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, saveAuth } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { BarChart3 } from "lucide-react";

export default function AgencyLogin() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "harry@glowleads.com", password: "agency123" });
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    try {
      const r = await api.post("/auth/login", form);
      if (r.data.user.role !== "agency") throw new Error("This login is for agency owners only.");
      saveAuth(r.data.token, r.data.user);
      navigate("/agency");
    } catch (e) {
      toast.error(e.response?.data?.detail || e.message || "Login failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="agency-theme min-h-screen flex items-center justify-center px-4" data-testid="agency-login-page">
      <div className="w-full max-w-md agency-card p-8 rounded-2xl">
        <Link to="/" className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-lg bg-[#00B4D8] flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">GlowLeads Console</span>
        </Link>
        <h1 className="text-2xl font-bold text-white mb-2">Agency sign in</h1>
        <p className="text-sm text-[#778DA9] mb-6">Master control for all your nail tech clients.</p>
        <div className="space-y-4">
          <div>
            <Label className="text-[#E0E1DD]">Email</Label>
            <Input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1 bg-[#0D1B2A] text-white border-[#415A77]" data-testid="agency-email-input" />
          </div>
          <div>
            <Label className="text-[#E0E1DD]">Password</Label>
            <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="mt-1 bg-[#0D1B2A] text-white border-[#415A77]" data-testid="agency-password-input" />
          </div>
          <Button
            className="w-full bg-[#00B4D8] hover:bg-[#0096b8] text-[#0D1B2A] font-semibold py-6"
            onClick={submit}
            disabled={loading}
            data-testid="agency-submit-btn"
          >
            {loading ? "..." : "Sign in"}
          </Button>
        </div>
        <div className="text-xs text-[#778DA9] mt-6 text-center border-t border-[#415A77] pt-4">
          Demo: <span className="font-mono">harry@glowleads.com / agency123</span>
        </div>
      </div>
    </div>
  );
}
