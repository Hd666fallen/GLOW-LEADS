import { useEffect, useState } from "react";
import { Routes, Route, NavLink, useNavigate, Navigate } from "react-router-dom";
import { api, currentUser, currentToken, clearAuth, verifyAuth, saveAuth } from "@/lib/api";
import { toast } from "sonner";
import {
  Home as HomeIcon, Calendar, Users, Settings as SettingsIcon,
  LogOut, Sparkles, Phone, MessageSquare, Share2, Copy, Check, Star, X, ImagePlus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import StyleImage from "@/components/StyleImage";

export default function TechDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(currentUser());
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const token = currentToken();
    if (!token) { navigate("/tech/login"); return; }
    verifyAuth().then((u) => {
      if (!u || u.role !== "tech") { navigate("/tech/login"); return; }
      setUser(u);
      setAuthChecked(true);
    });
  }, [navigate]);

  if (!authChecked || !user || user.role !== "tech") {
    return <div className="tech-theme flex items-center justify-center h-screen text-sm text-gray-400">Loading...</div>;
  }

  return (
    <div className="tech-theme" data-testid="tech-dashboard">
      <div className="max-w-md mx-auto h-[100dvh] flex flex-col relative overflow-hidden bg-white shadow-xl">
        <div className="flex-1 overflow-y-auto pb-20">
          <Routes>
            <Route index element={<HomeTab user={user} />} />
            <Route path="appointments" element={<AppointmentsTab />} />
            <Route path="leads" element={<LeadsTab />} />
            <Route path="settings" element={<SettingsTab user={user} />} />
            <Route path="*" element={<Navigate to="/tech" replace />} />
          </Routes>
        </div>
        <BottomNav />
      </div>
    </div>
  );
}

function BottomNav() {
  const base = "flex-1 flex flex-col items-center justify-center gap-1 text-xs";
  return (
    <nav className="absolute bottom-0 left-0 right-0 h-16 bg-white border-t flex items-stretch" data-testid="tech-bottom-nav">
      {[
        { to: "/tech", icon: HomeIcon, label: "Home", testid: "nav-home", exact: true },
        { to: "/tech/appointments", icon: Calendar, label: "Appts", testid: "nav-appointments" },
        { to: "/tech/leads", icon: Users, label: "Leads", testid: "nav-leads" },
        { to: "/tech/settings", icon: SettingsIcon, label: "Settings", testid: "nav-settings" },
      ].map((n) => (
        <NavLink
          key={n.to} to={n.to} end={n.exact}
          className={({ isActive }) => `${base} ${isActive ? "text-[#B76E79]" : "text-gray-400"}`}
          data-testid={n.testid}
        >
          <n.icon className="w-5 h-5" />
          <span>{n.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

function HomeTab({ user }) {
  const [stats, setStats] = useState(null);
  const [copied, setCopied] = useState(false);
  useEffect(() => { api.get("/tech/me/stats").then((r) => setStats(r.data)); }, []);

  const link = `${window.location.origin}/try/${user.slug}`;

  const hour = new Date().getHours();
  const greet = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="px-5 pt-8" data-testid="tech-home-tab">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-serif text-2xl font-bold">{greet}, {user.full_name.split(" ")[0]} 💅</h1>
          <p className="text-xs text-gray-500">{stats?.today}</p>
        </div>
        <button onClick={() => { clearAuth(); window.location.href = "/"; }} className="text-gray-400 hover:text-[#B76E79]" data-testid="logout-btn">
          <LogOut className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-6">
        <StatCard label="New leads" value={stats?.leads_today ?? "-"} testid="stat-leads" />
        <StatCard label="This week" value={stats?.appts_this_week ?? "-"} testid="stat-appts" />
        <StatCard label="Revenue" value={`$${stats?.revenue_this_month ?? 0}`} testid="stat-revenue" />
      </div>

      <div className="tech-card p-5 mb-5 bg-gradient-to-br from-[#FADADD]/30 to-white border-2 border-[#C2185B]/20" data-testid="funnel-link-card">
        <p className="text-xs text-[#C2185B] uppercase tracking-wider font-semibold mb-3">Your funnel link</p>
        <div className="flex items-center gap-2 bg-white rounded-xl p-3 text-sm break-all shadow-sm border border-pink-100">
          <span className="flex-1 truncate font-semibold text-gray-800" data-testid="booking-link">{link}</span>
          <button
            onClick={() => { navigator.clipboard.writeText(link); setCopied(true); toast.success("Copied!"); setTimeout(() => setCopied(false), 1500); }}
            className="p-2 hover:bg-pink-50 rounded-lg shrink-0"
            data-testid="copy-link-btn"
            aria-label="Copy funnel link"
          >
            {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4 text-[#C2185B]" />}
          </button>
        </div>
        <div className="grid grid-cols-[auto_1fr] gap-4 mt-4 items-center">
          <img
            src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(link)}`}
            alt="Funnel QR code"
            className="w-[110px] h-[110px] rounded-xl border border-pink-200 bg-white p-1"
            data-testid="funnel-qr-code"
          />
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full rounded-full border-[#C2185B] text-[#C2185B] hover:bg-[#C2185B] hover:text-white"
              onClick={() => window.open(link, "_blank")}
              data-testid="preview-funnel-btn"
            >
              <Share2 className="w-4 h-4 mr-2" /> Preview my funnel
            </Button>
            <p className="text-[11px] text-gray-500 leading-snug">
              Scan or share this QR on your Instagram bio, business card or front desk.
            </p>
          </div>
        </div>
      </div>

      <div className="tech-card p-5 mb-5" data-testid="activity-card">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Live activity</p>
          {stats?.automation_stats?.sms_this_week !== undefined && (
            <span className="text-[10px] text-[#B76E79] font-semibold bg-[#FADADD]/40 px-2 py-1 rounded-full">
              🤖 {stats.automation_stats.sms_this_week} auto SMS this week
            </span>
          )}
        </div>
        <div className="space-y-3 max-h-80 overflow-y-auto" data-testid="activity-feed">
          {(stats?.activity || []).map((a, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <span className="text-lg leading-tight">{a.icon || (a.type === "booking" ? "🎉" : "👀")}</span>
              <div className="flex-1 min-w-0">
                <p className="leading-snug">{a.text}</p>
                <p className="text-[10px] text-gray-400 mt-0.5">{formatWhen(a.when)}</p>
              </div>
            </div>
          ))}
          {(!stats?.activity || stats.activity.length === 0) && (
            <p className="text-sm text-gray-400">No activity yet — share your booking link!</p>
          )}
        </div>
      </div>
    </div>
  );
}

function formatWhen(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`;
    return d.toLocaleDateString();
  } catch {
    return "";
  }
}

function StatCard({ label, value, testid }) {
  return (
    <div className="tech-card p-3 text-center" data-testid={testid}>
      <p className="text-2xl font-bold text-[#B76E79]">{value}</p>
      <p className="text-[10px] uppercase tracking-wider text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function AppointmentsTab() {
  const [appts, setAppts] = useState([]);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try {
      const r = await api.get("/tech/me/appointments");
      setAppts(r.data.appointments);
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const setStatus = async (id, status) => {
    try { await api.put(`/tech/me/appointments/${id}`, { status }); await load(); toast.success(`Marked ${status}`); }
    catch { toast.error("Couldn't update"); }
  };

  const now = Date.now();
  const isPast = (a) => {
    try {
      const t = new Date(`${a.date}T${a.time}:00`).getTime();
      return t < now;
    } catch { return false; }
  };

  return (
    <div className="px-5 pt-8" data-testid="tech-appts-tab">
      <h1 className="font-serif text-2xl font-bold mb-1">Appointments</h1>
      <p className="text-xs text-gray-500 mb-5">Tap Complete or Cancel — or swipe on mobile</p>
      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map((i) => <div key={i} className="tech-card p-4 h-24 animate-pulse bg-gray-100" />)}
        </div>
      ) : (
        <div className="space-y-3">
          {appts.map((a) => (
            <div key={a.id} className="tech-card p-4" data-testid={`appt-card-${a.id}`}>
              <div className="flex items-start gap-3">
                <img src={a.preview_image} alt="" className="w-16 h-16 rounded-xl object-cover" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold truncate">{a.client_name}</p>
                    <Badge variant="secondary" className={
                      a.status === "completed" ? "bg-green-100 text-green-700" :
                      a.status === "confirmed" ? "bg-blue-100 text-blue-700" :
                      a.status === "cancelled" ? "bg-red-100 text-red-700" :
                      a.status === "no-show" ? "bg-red-100 text-red-700" :
                      "bg-amber-100 text-amber-700"
                    }>{a.status}</Badge>
                    {a.status === "confirmed" && isPast({...a}) === false && (
                      <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">📅 Reminder scheduled</span>
                    )}
                    {a.status === "completed" && (
                      <span className="text-[10px] bg-[#FADADD]/60 text-[#B76E79] px-2 py-0.5 rounded-full">⭐ Review requested</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{a.style_name}</p>
                  <p className="text-xs text-gray-500">{a.date} at {a.time} · ${a.price}</p>
                  <div className="flex gap-2 mt-2">
                    <a href={`tel:${a.client_phone}`} className="text-xs bg-gray-100 px-3 py-1.5 rounded-full flex items-center gap-1" data-testid={`call-${a.id}`}>
                      <Phone className="w-3 h-3" /> Call
                    </a>
                    <a href={`sms:${a.client_phone}`} className="text-xs bg-gray-100 px-3 py-1.5 rounded-full flex items-center gap-1" data-testid={`sms-${a.id}`}>
                      <MessageSquare className="w-3 h-3" /> Text
                    </a>
                  </div>
                </div>
              </div>
              {a.status !== "completed" && a.status !== "cancelled" && a.status !== "no-show" && (
                <div className="grid grid-cols-2 gap-2 mt-3">
                  <Button variant="outline" size="sm" className="rounded-full" onClick={() => setStatus(a.id, "cancelled")} data-testid={`cancel-${a.id}`}>Cancel</Button>
                  <Button size="sm" className="rounded-full rose-gold-gradient" onClick={() => setStatus(a.id, "completed")} data-testid={`complete-${a.id}`}>Mark complete</Button>
                </div>
              )}
            </div>
          ))}
          {appts.length === 0 && <p className="text-center text-sm text-gray-400 py-10">No appointments yet — share your booking link! 💅</p>}
        </div>
      )}
    </div>
  );
}

function LeadsTab() {
  const [data, setData] = useState({ leads: [], winback: [], stats: {} });
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try {
      const r = await api.get("/tech/me/leads");
      setData(r.data);
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const followUp = async (id) => {
    try { await api.post(`/tech/me/leads/${id}/follow-up`); toast.success("Follow-up sent 📱"); await load(); }
    catch { toast.error("Could not send"); }
  };

  const s = data.stats || {};
  const tempBadge = (t) => {
    if (t === "hot") return { label: "Hot 🔥", cls: "bg-red-100 text-red-700" };
    if (t === "warm") return { label: "Warm 💛", cls: "bg-amber-100 text-amber-700" };
    return { label: "Cold 🧊", cls: "bg-slate-100 text-slate-600" };
  };

  return (
    <div className="px-5 pt-8" data-testid="tech-leads-tab">
      <h1 className="font-serif text-2xl font-bold mb-1">Leads</h1>
      <p className="text-xs text-gray-500 mb-4">Auto-nurtured by the system — you can still send a manual follow-up.</p>

      <div className="tech-card p-4 mb-5 text-sm flex justify-between">
        <Stat label="Tried" value={s.total_tryons ?? 0} />
        <Stat label="Booked %" value={`${s.conversion_pct ?? 0}%`} />
        <Stat label="Follow-ups" value={s.followups_sent ?? 0} />
      </div>

      {loading ? (
        <div className="space-y-3">{[1,2,3].map((i) => <div key={i} className="tech-card h-20 animate-pulse bg-gray-100" />)}</div>
      ) : (
        <>
          <div className="space-y-3">
            {data.leads.map((l) => {
              const b = tempBadge(l.temperature);
              return (
                <div key={l.id} className="tech-card p-4 flex items-start gap-3" data-testid={`lead-card-${l.id}`}>
                  <img src={l.preview_image} alt="" className="w-14 h-14 rounded-xl object-cover" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-semibold truncate">{l.name}</p>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full ${b.cls}`} data-testid={`lead-temp-${l.id}`}>{b.label}</span>
                    </div>
                    <p className="text-xs text-gray-500">{l.style_name}</p>
                    <p className="text-[10px] text-gray-400 mt-0.5">{formatWhen(l.created_at)} · {l.follow_ups_sent || 0} auto follow-ups sent</p>
                    {l.temperature !== "cold" && (
                      <Button size="sm" className="rounded-full rose-gold-gradient mt-2" onClick={() => followUp(l.id)} data-testid={`followup-${l.id}`}>
                        <MessageSquare className="w-3 h-3 mr-2" /> Send follow-up now
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
            {data.leads.length === 0 && <p className="text-center text-sm text-gray-400 py-10">No leads yet.</p>}
          </div>

          {data.winback && data.winback.length > 0 && (
            <div className="mt-6" data-testid="winback-section">
              <div className="flex items-center gap-2 mb-3">
                <h2 className="font-serif text-lg font-bold">Win-back 💌</h2>
                <span className="text-[10px] text-[#B76E79] bg-[#FADADD]/40 px-2 py-0.5 rounded-full">30+ days inactive</span>
              </div>
              <p className="text-xs text-gray-500 mb-3">System auto-sent these a re-engagement SMS.</p>
              <div className="space-y-2">
                {data.winback.map((l) => (
                  <div key={l.id} className="tech-card p-3 flex items-center gap-3" data-testid={`winback-card-${l.id}`}>
                    <img src={l.preview_image} alt="" className="w-10 h-10 rounded-lg object-cover" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold truncate">{l.name}</p>
                      <p className="text-[10px] text-gray-500">{l.style_name} · {formatWhen(l.created_at)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-center flex-1">
      <p className="font-bold text-[#B76E79] text-lg">{value}</p>
      <p className="text-[10px] uppercase tracking-wider text-gray-500">{label}</p>
    </div>
  );
}

function SettingsTab({ user }) {
  return (
    <div className="px-5 pt-8" data-testid="tech-settings-tab">
      <h1 className="font-serif text-2xl font-bold mb-4">Settings</h1>
      <Tabs defaultValue="page">
        <TabsList className="grid grid-cols-5 mb-4">
          <TabsTrigger value="page" data-testid="tab-page">Page</TabsTrigger>
          <TabsTrigger value="styles" data-testid="tab-styles">Styles</TabsTrigger>
          <TabsTrigger value="avail" data-testid="tab-avail">Hours</TabsTrigger>
          <TabsTrigger value="automations" data-testid="tab-automations">Auto</TabsTrigger>
          <TabsTrigger value="account" data-testid="tab-account">Account</TabsTrigger>
        </TabsList>
        <TabsContent value="page" forceMount className="data-[state=inactive]:hidden"><MyPage user={user} /></TabsContent>
        <TabsContent value="styles" forceMount className="data-[state=inactive]:hidden"><StyleManager /></TabsContent>
        <TabsContent value="avail" forceMount className="data-[state=inactive]:hidden"><Availability /></TabsContent>
        <TabsContent value="automations" forceMount className="data-[state=inactive]:hidden"><AutomationsPanel /></TabsContent>
        <TabsContent value="account" forceMount className="data-[state=inactive]:hidden"><AccountPanel user={user} /></TabsContent>
      </Tabs>
    </div>
  );
}

function MyPage({ user }) {
  const [p, setP] = useState({
    full_name: user.full_name, business_name: user.business_name,
    bio: user.bio, city: user.city, phone: user.phone, profile_photo: user.profile_photo,
  });
  const save = async () => {
    try { await api.put("/tech/me/profile", p); toast.success("Profile saved"); }
    catch { toast.error("Couldn't save"); }
  };
  return (
    <div className="tech-card p-5 space-y-3" data-testid="my-page-panel">
      <div className="flex items-center gap-3">
        <img src={p.profile_photo} alt="" className="w-16 h-16 rounded-full object-cover" />
        <Input value={p.profile_photo} onChange={(e) => setP({ ...p, profile_photo: e.target.value })} placeholder="Photo URL" data-testid="profile-photo-input" />
      </div>
      <div><Label>Business name</Label><Input value={p.business_name} onChange={(e) => setP({ ...p, business_name: e.target.value })} data-testid="profile-business-input" /></div>
      <div><Label>City</Label><Input value={p.city} onChange={(e) => setP({ ...p, city: e.target.value })} data-testid="profile-city-input" /></div>
      <div><Label>Bio</Label><Textarea value={p.bio} onChange={(e) => setP({ ...p, bio: e.target.value })} rows={3} data-testid="profile-bio-input" /></div>
      <Button onClick={save} className="w-full rounded-full rose-gold-gradient" data-testid="profile-save-btn">Save</Button>
    </div>
  );
}

function StyleManager() {
  const [data, setData] = useState({ all: [], enabled_ids: [], style_photos: {} });
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("ALL");
  const [prices, setPrices] = useState({});
  const [uploading, setUploading] = useState(null);
  useEffect(() => { api.get("/tech/me/styles").then((r) => setData({ style_photos: {}, ...r.data })); }, []);

  const toggle = async (id) => {
    const enabled = new Set(data.enabled_ids);
    if (enabled.has(id)) enabled.delete(id); else enabled.add(id);
    const next = Array.from(enabled);
    setData({ ...data, enabled_ids: next });
    try { await api.put("/tech/me/styles", { enabled_style_ids: next }); }
    catch { toast.error("Couldn't update"); }
  };

  const uploadPhoto = async (styleId, file) => {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { toast.error("Max 5MB"); return; }
    setUploading(styleId);
    try {
      const fd = new FormData();
      fd.append("style_id", styleId);
      fd.append("file", file);
      const r = await api.post("/tech/me/style-photo", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setData((d) => ({ ...d, style_photos: { ...(d.style_photos || {}), [styleId]: r.data.url } }));
      toast.success("Photo uploaded ✨");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(null);
    }
  };

  const removePhoto = async (styleId) => {
    try {
      await api.delete(`/tech/me/style-photo/${styleId}`);
      setData((d) => {
        const next = { ...(d.style_photos || {}) };
        delete next[styleId];
        return { ...d, style_photos: next };
      });
      toast.success("Photo removed");
    } catch {
      toast.error("Couldn't remove");
    }
  };

  const enabledSet = new Set(data.enabled_ids);
  const cats = ["ALL", "FINISHES", "FRENCH", "OMBRE", "NAIL_ART", "EMBELLISHMENTS", "COLORS", "SPECIALTY"];
  const filtered = data.all.filter((s) =>
    (cat === "ALL" || s.category === cat) &&
    (!q || s.name.toLowerCase().includes(q.toLowerCase()))
  );
  const catLabel = (c) => ({
    ALL: "All",
    FINISHES: "Finishes", FRENCH: "French", OMBRE: "Ombre",
    NAIL_ART: "Art", EMBELLISHMENTS: "Gems", COLORS: "Colors", SPECIALTY: "Specialty",
  }[c] || c);

  const absolutise = (url) => (url && url.startsWith("/api/") ? `${process.env.REACT_APP_BACKEND_URL}${url}` : url);

  return (
    <div data-testid="style-manager-panel">
      <div className="tech-card p-4 mb-3">
        <Input placeholder="Search styles..." value={q} onChange={(e) => setQ(e.target.value)} data-testid="style-search-input" />
        <div className="flex gap-1.5 overflow-x-auto no-scrollbar mt-3 pb-1">
          {cats.map((c) => (
            <button
              key={c} onClick={() => setCat(c)}
              className={`shrink-0 text-xs px-3 py-1.5 rounded-full font-semibold ${
                cat === c ? "bg-[#B76E79] text-white" : "bg-gray-100 text-gray-600"
              }`}
              data-testid={`style-cat-${c}`}
            >
              {catLabel(c)}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2" data-testid="style-counter">
          {enabledSet.size} of {data.all.length} styles enabled
        </p>
      </div>

      <div className="space-y-2 overflow-y-auto h-[calc(100vh-120px)] max-h-[calc(100vh-120px)] pr-1">
        {filtered.map((s) => {
          const on = enabledSet.has(s.id);
          const price = prices[s.id] ?? s.price_range.low;
          const customUrl = data.style_photos?.[s.id];
          const isUploading = uploading === s.id;
          return (
            <div key={s.id} className="tech-card p-3 flex items-center gap-3" data-testid={`style-row-${s.id}`}>
              <div className="relative w-12 h-12 shrink-0">
                {customUrl ? (
                  <img src={absolutise(customUrl)} alt={s.name} className="w-12 h-12 rounded-lg object-cover ring-2 ring-[#C2185B]" data-testid={`style-thumb-${s.id}`} />
                ) : (
                  <StyleImage src={s.image} category={s.category} className="w-12 h-12 rounded-lg object-cover" data-testid={`style-thumb-${s.id}`} />
                )}
                {customUrl && (
                  <button
                    onClick={() => removePhoto(s.id)}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-red-500 text-white flex items-center justify-center shadow hover:bg-red-600"
                    title="Remove photo"
                    data-testid={`remove-photo-${s.id}`}
                  >
                    <X className="w-3 h-3" strokeWidth={3} />
                  </button>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold truncate">{s.name}</p>
                  <span className="text-[9px] bg-gray-100 text-gray-500 uppercase tracking-wider px-1.5 py-0.5 rounded">{catLabel(s.category)}</span>
                  {customUrl && <span className="text-[9px] bg-[#C2185B] text-white uppercase tracking-wider px-1.5 py-0.5 rounded">Her work ✨</span>}
                </div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="text-[10px] text-gray-400">Price $</span>
                  <input
                    type="number" value={price}
                    onChange={(e) => setPrices({ ...prices, [s.id]: e.target.value })}
                    className="w-16 text-xs border rounded px-2 py-0.5"
                    data-testid={`price-${s.id}`}
                  />
                  <label
                    className={`text-[10px] inline-flex items-center gap-1 text-[#B76E79] underline cursor-pointer ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
                    data-testid={`upload-photo-${s.id}`}
                  >
                    <ImagePlus className="w-3 h-3" />
                    {isUploading ? "Uploading..." : (customUrl ? "Replace photo" : "Upload photo")}
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      className="hidden"
                      onChange={(e) => { const f = e.target.files?.[0]; e.target.value = ""; if (f) uploadPhoto(s.id, f); }}
                      data-testid={`upload-input-${s.id}`}
                    />
                  </label>
                </div>
              </div>
              <Switch checked={on} onCheckedChange={() => toggle(s.id)} data-testid={`style-toggle-${s.id}`} />
            </div>
          );
        })}
        {filtered.length === 0 && <p className="text-center text-sm text-gray-400 py-6">No styles match.</p>}
      </div>
    </div>
  );
}

function AutomationsPanel() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get("/tech/me/automations").then((r) => setData(r.data)); }, []);

  const update = async (key, val) => {
    const next = { ...data.settings, [key]: val };
    setData({ ...data, settings: next });
    try { await api.put("/tech/me/automations", next); toast.success("Saved"); }
    catch { toast.error("Couldn't save"); }
  };

  if (!data) return <p className="text-sm text-gray-500">Loading...</p>;

  const rows = [
    { key: "instant_booking", title: "Instant booking confirmation", desc: "SMS sent the moment a customer books." },
    { key: "reminder_24h", title: "24-hour appointment reminder", desc: "Reminder SMS 1 day before appointment." },
    { key: "reminder_1h", title: "1-hour appointment reminder", desc: "Final reminder 1 hour before arrival." },
    { key: "review_request", title: "Post-appointment review request", desc: "Sent 2h after you mark an appointment complete." },
    { key: "noshow_recovery", title: "No-show recovery SMS", desc: "Win them back if they don't arrive." },
    { key: "lead_sequence", title: "Lead follow-up sequence (Day 0, 2, 5)", desc: "Auto nurtures try-on leads into bookings." },
    { key: "winback", title: "30-day win-back campaign", desc: "Re-engage past clients who haven't booked in 30+ days." },
  ];

  return (
    <div data-testid="automations-panel">
      <div className="tech-card p-4 mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">🤖</span>
          <h2 className="font-serif text-lg font-bold">Automation Center</h2>
        </div>
        <p className="text-xs text-gray-500">Your robot assistant — running 24/7. Toggle anything off if you prefer.</p>
      </div>

      <div className="space-y-2">
        {rows.map((r) => (
          <div key={r.key} className="tech-card p-4 flex items-start gap-3" data-testid={`automation-${r.key}`}>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold">{r.title}</p>
              <p className="text-xs text-gray-500 mt-0.5">{r.desc}</p>
            </div>
            <Switch checked={!!data.settings[r.key]} onCheckedChange={(v) => update(r.key, v)} data-testid={`toggle-${r.key}`} />
          </div>
        ))}
      </div>

      <div className="tech-card p-4 mt-4" data-testid="automation-stats">
        <p className="text-xs uppercase tracking-wider text-gray-500 mb-2">This week, automatically</p>
        <div className="flex justify-between">
          <Stat label="SMS sent" value={data.stats.sms_this_week} />
          <Stat label="Leads nurtured" value={data.stats.followups_this_week} />
          <Stat label="Reviews asked" value={data.stats.reviews_this_week} />
        </div>
      </div>
    </div>
  );
}

function Availability() {
  const [days, setDays] = useState({ Mon: true, Tue: true, Wed: true, Thu: true, Fri: true, Sat: true, Sun: false });
  return (
    <div className="tech-card p-5 space-y-3" data-testid="availability-panel">
      <p className="text-sm font-semibold">Working days</p>
      {Object.entries(days).map(([d, on]) => (
        <div key={d} className="flex items-center justify-between">
          <span className="text-sm">{d}</span>
          <Switch checked={on} onCheckedChange={(v) => setDays({ ...days, [d]: v })} />
        </div>
      ))}
      <div className="pt-3 text-xs text-gray-500">Connect Google Calendar — coming soon</div>
    </div>
  );
}

function AccountPanel({ user }) {
  return (
    <div className="tech-card p-5 space-y-3" data-testid="account-panel">
      <p className="text-sm">Email: <span className="font-semibold">{user.email}</span></p>
      <p className="text-sm">Plan: <span className="font-semibold capitalize">{user.plan || "starter"}</span></p>
      <p className="text-sm flex items-center gap-1">Rating: <Star className="w-3 h-3 fill-[#FFD700] text-[#FFD700]" /> <span className="font-semibold">{user.rating}</span> ({user.review_count} reviews)</p>
      <Button variant="outline" className="w-full rounded-full" onClick={() => { clearAuth(); window.location.href = "/"; }} data-testid="account-logout-btn">
        Log out
      </Button>
    </div>
  );
}
