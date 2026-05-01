import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, saveAuth } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Sparkles } from "lucide-react";

export default function TechLogin() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    email: "sophie@glowleads.com",
    password: "sophie123",
    full_name: "",
    business_name: "",
    city: "",
    phone: "",
  });
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    try {
      const r = mode === "login"
        ? await api.post("/auth/login", { email: form.email, password: form.password })
        : await api.post("/auth/register", form);
      saveAuth(r.data.token, r.data.user);
      if (r.data.user.role === "agency") return navigate("/agency");
      navigate("/tech");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Login failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#fce4ec] via-white to-[#fce4ec] flex items-center justify-center px-4" data-testid="tech-login-page">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8">
        <Link to="/" className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-full bg-[#C2185B] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-[#FFD700]" />
          </div>
          <span className="font-serif text-xl font-bold text-[#C2185B]">GlowLeads</span>
        </Link>
        <h1 className="font-serif text-3xl font-bold mb-2">{mode === "login" ? "Welcome back" : "Create your account"}</h1>
        <p className="text-sm text-gray-500 mb-6">{mode === "login" ? "Log in to your GlowLeads dashboard" : "Start turning try-ons into bookings"}</p>

        <div className="space-y-4">
          {mode === "register" && (
            <>
              <Field label="Full name" value={form.full_name} onChange={(v) => setForm({ ...form, full_name: v })} tid="register-name" />
              <Field label="Business name" value={form.business_name} onChange={(v) => setForm({ ...form, business_name: v })} tid="register-business" />
              <Field label="City" value={form.city} onChange={(v) => setForm({ ...form, city: v })} tid="register-city" />
              <Field label="Phone (optional)" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} tid="register-phone" />
            </>
          )}
          <Field label="Email" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} tid="login-email" />
          <Field label="Password" type="password" value={form.password} onChange={(v) => setForm({ ...form, password: v })} tid="login-password" />

          <Button
            className="w-full rounded-full bg-[#C2185B] hover:bg-[#a0144a] text-white py-6 font-semibold"
            onClick={submit}
            disabled={loading}
            data-testid="login-submit-btn"
          >
            {loading ? "..." : mode === "login" ? "Log in" : "Create account"}
          </Button>
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            className="w-full text-sm text-gray-500 hover:text-[#C2185B]"
            data-testid="toggle-mode-btn"
          >
            {mode === "login" ? "New here? Create an account" : "Already have an account? Log in"}
          </button>
        </div>

        <div className="text-xs text-gray-400 mt-6 text-center border-t pt-4">
          Demo login: <span className="font-mono">sophie@glowleads.com / sophie123</span>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text", tid }) {
  return (
    <div>
      <Label>{label}</Label>
      <Input type={type} value={value} onChange={(e) => onChange(e.target.value)} className="mt-1" data-testid={tid} />
    </div>
  );
}
