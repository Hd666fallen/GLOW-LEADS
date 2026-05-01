import { useEffect, useState } from "react";
import { Routes, Route, NavLink, useNavigate, Navigate } from "react-router-dom";
import { api, currentUser, clearAuth } from "@/lib/api";
import { toast } from "sonner";
import {
  Home as HomeIcon, Calendar, Users, Settings as SettingsIcon,
  LogOut, Sparkles, Phone, MessageSquare, Share2, Copy, Check, Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function TechDashboard() {
  const navigate = useNavigate();
  const user = currentUser();
  useEffect(() => {
    if (!user || user.role !== "tech") navigate("/tech/login");
  }, [user, navigate]);
  if (!user || user.role !== "tech") return null;

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

      <div className="tech-card p-5 mb-5">
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Live activity</p>
        <div className="space-y-3 max-h-64 overflow-y-auto" data-testid="activity-feed">
          {(stats?.activity || []).map((a, i) => (
            <div key={i} className="flex items-start gap-3 text-sm">
              <span className="text-lg">{a.type === "booking" ? "🎉" : "👀"}</span>
              <p>{a.text}</p>
            </div>
          ))}
          {(!stats?.activity || stats.activity.length === 0) && (
            <p className="text-sm text-gray-400">No activity yet — share your booking link!</p>
          )}
        </div>
      </div>

      <div className="tech-card p-5">
        <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Your booking link</p>
        <div className="flex items-center gap-2 bg-gray-50 rounded-xl p-3 text-sm break-all">
          <span className="flex-1 truncate" data-testid="booking-link">{link}</span>
          <button
            onClick={() => { navigator.clipboard.writeText(link); setCopied(true); toast.success("Copied!"); setTimeout(() => setCopied(false), 1500); }}
            className="p-2 hover:bg-gray-200 rounded-lg"
            data-testid="copy-link-btn"
          >
            {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-3">
          <Button variant="outline" className="rounded-full" onClick={() => window.open(link, "_blank")} data-testid="preview-page-btn">
            <Share2 className="w-4 h-4 mr-2" /> Preview page
          </Button>
          <Button className="rounded-full rose-gold-gradient" data-testid="send-promo-btn">
            <Sparkles className="w-4 h-4 mr-2" /> Send promo
          </Button>
        </div>
      </div>
    </div>
  );
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
  const load = () => api.get("/tech/me/appointments").then((r) => setAppts(r.data.appointments));
  useEffect(() => { load(); }, []);

  const setStatus = async (id, status) => {
    try { await api.put(`/tech/me/appointments/${id}`, { status }); await load(); toast.success(`Marked ${status}`); }
    catch { toast.error("Couldn't update"); }
  };

  return (
    <div className="px-5 pt-8" data-testid="tech-appts-tab">
      <h1 className="font-serif text-2xl font-bold mb-1">Appointments</h1>
      <p className="text-xs text-gray-500 mb-5">Swipe-style actions: tap Complete or Cancel</p>
      <div className="space-y-3">
        {appts.map((a) => (
          <div key={a.id} className="tech-card p-4" data-testid={`appt-card-${a.id}`}>
            <div className="flex items-start gap-3">
              <img src={a.preview_image} alt="" className="w-16 h-16 rounded-xl object-cover" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-semibold truncate">{a.client_name}</p>
                  <Badge variant={a.status === "completed" ? "default" : "secondary"} className={
                    a.status === "completed" ? "bg-green-100 text-green-700" :
                    a.status === "confirmed" ? "bg-blue-100 text-blue-700" :
                    a.status === "cancelled" ? "bg-red-100 text-red-700" :
                    "bg-amber-100 text-amber-700"
                  }>{a.status}</Badge>
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
            {a.status !== "completed" && a.status !== "cancelled" && (
              <div className="grid grid-cols-2 gap-2 mt-3">
                <Button variant="outline" size="sm" className="rounded-full" onClick={() => setStatus(a.id, "cancelled")} data-testid={`cancel-${a.id}`}>Cancel</Button>
                <Button size="sm" className="rounded-full rose-gold-gradient" onClick={() => setStatus(a.id, "completed")} data-testid={`complete-${a.id}`}>Mark complete</Button>
              </div>
            )}
          </div>
        ))}
        {appts.length === 0 && <p className="text-center text-sm text-gray-400 py-10">No appointments yet — share your booking link! 💅</p>}
      </div>
    </div>
  );
}

function LeadsTab() {
  const [data, setData] = useState({ leads: [], stats: {} });
  const load = () => api.get("/tech/me/leads").then((r) => setData(r.data));
  useEffect(() => { load(); }, []);

  const followUp = async (id) => {
    try { const r = await api.post(`/tech/me/leads/${id}/follow-up`); toast.success("Follow-up sent 📱"); await load(); }
    catch { toast.error("Could not send"); }
  };

  const s = data.stats || {};
  return (
    <div className="px-5 pt-8" data-testid="tech-leads-tab">
      <h1 className="font-serif text-2xl font-bold mb-1">Leads</h1>
      <p className="text-xs text-gray-500 mb-4">People who tried your styles but haven&apos;t booked yet.</p>

      <div className="tech-card p-4 mb-5 text-sm flex justify-between">
        <Stat label="Tried" value={s.total_tryons ?? 0} />
        <Stat label="Booked %" value={`${s.conversion_pct ?? 0}%`} />
        <Stat label="Follow-ups" value={s.followups_sent ?? 0} />
      </div>

      <div className="space-y-3">
        {data.leads.map((l) => (
          <div key={l.id} className="tech-card p-4 flex items-start gap-3" data-testid={`lead-card-${l.id}`}>
            <img src={l.preview_image} alt="" className="w-14 h-14 rounded-xl object-cover" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{l.name}</p>
              <p className="text-xs text-gray-500">{l.style_name}</p>
              <p className="text-xs text-amber-600 mt-1">Not booked yet</p>
              <Button size="sm" className="rounded-full rose-gold-gradient mt-2" onClick={() => followUp(l.id)} data-testid={`followup-${l.id}`}>
                <MessageSquare className="w-3 h-3 mr-2" /> Send follow-up
              </Button>
            </div>
          </div>
        ))}
        {data.leads.length === 0 && <p className="text-center text-sm text-gray-400 py-10">No leads yet.</p>}
      </div>
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
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="page" data-testid="tab-page">Page</TabsTrigger>
          <TabsTrigger value="styles" data-testid="tab-styles">Styles</TabsTrigger>
          <TabsTrigger value="avail" data-testid="tab-avail">Hours</TabsTrigger>
          <TabsTrigger value="account" data-testid="tab-account">Account</TabsTrigger>
        </TabsList>
        <TabsContent value="page"><MyPage user={user} /></TabsContent>
        <TabsContent value="styles"><StyleManager /></TabsContent>
        <TabsContent value="avail"><Availability /></TabsContent>
        <TabsContent value="account"><AccountPanel user={user} /></TabsContent>
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
  const [data, setData] = useState({ all: [], enabled_ids: [] });
  useEffect(() => { api.get("/tech/me/styles").then((r) => setData(r.data)); }, []);
  const toggle = async (id) => {
    const enabled = new Set(data.enabled_ids);
    if (enabled.has(id)) enabled.delete(id); else enabled.add(id);
    const next = Array.from(enabled);
    setData({ ...data, enabled_ids: next });
    try { await api.put("/tech/me/styles", { enabled_style_ids: next }); }
    catch { toast.error("Couldn't update"); }
  };
  const enabledSet = new Set(data.enabled_ids);
  return (
    <div className="tech-card p-4" data-testid="style-manager-panel">
      <p className="text-xs text-gray-500 mb-3">Enable only the styles you offer. Customers will see these.</p>
      <div className="space-y-2 max-h-[60vh] overflow-y-auto">
        {data.all.map((s) => (
          <div key={s.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-xl" data-testid={`style-toggle-${s.id}`}>
            <img src={s.image} alt="" className="w-10 h-10 rounded-lg object-cover" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">{s.name}</p>
              <p className="text-[10px] text-gray-400">{s.category}</p>
            </div>
            <Switch checked={enabledSet.has(s.id)} onCheckedChange={() => toggle(s.id)} />
          </div>
        ))}
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
