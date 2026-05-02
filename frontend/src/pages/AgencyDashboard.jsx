import { useEffect, useState } from "react";
import { Routes, Route, NavLink, useNavigate, Navigate } from "react-router-dom";
import { api, currentUser, currentToken, clearAuth, verifyAuth } from "@/lib/api";
import {
  LayoutDashboard, Users, BarChart3, Sparkles, CreditCard, Settings as SettingsIcon,
  LogOut, AlertTriangle, TrendingUp, DollarSign, ShoppingBag, Zap,
} from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

const COLORS = ["#00B4D8", "#C2185B", "#FFD700", "#8ED6FB", "#FF4D9D", "#6DD5ED", "#F9C74F"];

export default function AgencyDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(currentUser());
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const token = currentToken();
    if (!token) { navigate("/agency/login"); return; }
    verifyAuth().then((u) => {
      if (!u || u.role !== "agency") { navigate("/agency/login"); return; }
      setUser(u);
      setAuthChecked(true);
    });
  }, [navigate]);

  if (!authChecked || !user || user.role !== "agency") {
    return <div className="agency-theme flex items-center justify-center h-screen text-sm text-[#778DA9]">Loading...</div>;
  }

  return (
    <div className="agency-theme flex h-screen overflow-hidden" data-testid="agency-dashboard">
      <Sidebar onLogout={() => { clearAuth(); navigate("/"); }} />
      <main className="flex-1 overflow-y-auto p-6 md:p-10">
        <Routes>
          <Route index element={<Overview />} />
          <Route path="clients" element={<Clients />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="style-intel" element={<StyleIntel />} />
          <Route path="billing" element={<Billing />} />
          <Route path="*" element={<Navigate to="/agency" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function Sidebar({ onLogout }) {
  const items = [
    { to: "/agency", icon: LayoutDashboard, label: "Overview", exact: true, tid: "sidebar-overview" },
    { to: "/agency/clients", icon: Users, label: "Clients", tid: "sidebar-clients" },
    { to: "/agency/analytics", icon: BarChart3, label: "Analytics", tid: "sidebar-analytics" },
    { to: "/agency/style-intel", icon: Sparkles, label: "Style Intel", tid: "sidebar-style-intel" },
    { to: "/agency/billing", icon: CreditCard, label: "Billing", tid: "sidebar-billing" },
  ];
  return (
    <aside className="w-60 flex-shrink-0 border-r border-[#415A77] bg-[#0D1B2A] p-5 flex flex-col" data-testid="agency-sidebar">
      <div className="flex items-center gap-2 mb-8">
        <div className="w-9 h-9 rounded-lg bg-[#00B4D8] flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-[#0D1B2A]" />
        </div>
        <span className="font-bold text-white">GlowLeads</span>
      </div>
      <nav className="flex-1 space-y-1">
        {items.map((n) => (
          <NavLink key={n.to} to={n.to} end={n.exact} data-testid={n.tid}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition ${
                isActive ? "bg-[#00B4D8]/15 text-[#00B4D8] border border-[#00B4D8]/40"
                : "text-[#E0E1DD] hover:bg-[#1B263B]"
              }`}>
            <n.icon className="w-4 h-4" /> {n.label}
          </NavLink>
        ))}
      </nav>
      <button onClick={onLogout} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-[#778DA9] hover:text-white hover:bg-[#1B263B]" data-testid="agency-logout-btn">
        <LogOut className="w-4 h-4" /> Log out
      </button>
    </aside>
  );
}

function KpiCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="agency-card p-5" data-testid={`kpi-${label.toLowerCase().replace(/ /g, "-")}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs uppercase tracking-wider text-[#778DA9]">{label}</span>
        <Icon className="w-4 h-4" style={{ color: accent }} />
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
    </div>
  );
}

function Overview() {
  const [data, setData] = useState(null);
  useEffect(() => { api.get("/agency/overview").then((r) => setData(r.data)); }, []);
  if (!data) return <p className="text-[#778DA9]">Loading...</p>;
  return (
    <div data-testid="agency-overview-page">
      <h1 className="text-2xl font-bold text-white mb-1">Overview</h1>
      <p className="text-sm text-[#778DA9] mb-6">Master control for all your nail tech clients</p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <KpiCard icon={Users} label="Active Clients" value={data.kpis.active_clients} accent="#00B4D8" />
        <KpiCard icon={Zap} label="Total Leads" value={data.kpis.total_leads} accent="#FFD700" />
        <KpiCard icon={ShoppingBag} label="Bookings" value={data.kpis.total_bookings} accent="#C2185B" />
        <KpiCard icon={DollarSign} label="MRR" value={`$${data.kpis.mrr}`} accent="#00B4D8" />
      </div>

      {data.at_risk.length > 0 && (
        <div className="agency-card p-5 mb-6 border-red-500/40 bg-red-900/15" data-testid="at-risk-banner">
          <div className="flex items-center gap-2 mb-3 text-red-300">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-semibold uppercase tracking-wider">Churn risk</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {data.at_risk.map((t) => (
              <div key={t.id} className="text-xs bg-[#1B263B] border border-red-500/30 rounded-lg px-3 py-2 text-white">
                {t.business_name} · {t.leads} leads · {t.city}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="agency-card p-5">
        <h3 className="font-semibold text-white mb-3">Recent activity</h3>
        <div className="space-y-2 text-sm">
          {data.activity.map((a, i) => (
            <div key={i} className="flex items-start gap-2 text-[#E0E1DD]">
              <span>{a.type === "booking" ? "🎉" : "👀"}</span> <span>{a.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Clients() {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  useEffect(() => { api.get("/agency/clients").then((r) => setRows(r.data.clients)); }, []);
  const filtered = rows.filter((r) =>
    !q || r.business_name.toLowerCase().includes(q.toLowerCase()) || r.city.toLowerCase().includes(q.toLowerCase())
  );
  return (
    <div data-testid="agency-clients-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Clients</h1>
          <p className="text-sm text-[#778DA9]">All nail techs on GlowLeads</p>
        </div>
        <input
          value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search..."
          className="bg-[#1B263B] border border-[#415A77] rounded-lg px-4 py-2 text-sm text-white placeholder-[#778DA9]"
          data-testid="clients-search-input"
        />
      </div>
      <div className="agency-card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-[#778DA9]">
            <tr className="border-b border-[#415A77]">
              <th className="p-4">Business</th><th className="p-4">Owner</th><th className="p-4">City</th>
              <th className="p-4">Plan</th><th className="p-4">Leads</th><th className="p-4">Bookings</th>
              <th className="p-4">MRR</th><th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-[#415A77]/50 hover:bg-[#415A77]/20 cursor-pointer" data-testid={`client-row-${r.id}`}>
                <td className="p-4 text-white">
                  <div className="flex items-center gap-2">
                    <img src={r.profile_photo} alt="" className="w-8 h-8 rounded-full object-cover" /> {r.business_name}
                  </div>
                </td>
                <td className="p-4">{r.owner_name}</td>
                <td className="p-4">{r.city}</td>
                <td className="p-4 capitalize">{r.plan}</td>
                <td className="p-4">{r.leads}</td>
                <td className="p-4">{r.bookings}</td>
                <td className="p-4">${r.mrr}</td>
                <td className="p-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    r.status === "active" ? "bg-green-900/40 text-green-300 border border-green-500/30" :
                    r.status === "at_risk" ? "bg-amber-900/40 text-amber-300 border border-amber-500/30" :
                    "bg-red-900/40 text-red-300 border border-red-500/30"
                  }`}>{r.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Analytics() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/agency/analytics").then((r) => setD(r.data)); }, []);
  if (!d) return <p className="text-[#778DA9]">Loading...</p>;

  const weekKeys = Object.keys(d.leads_weekly?.[0] || {}).filter((k) => k !== "week");
  return (
    <div data-testid="agency-analytics-page">
      <h1 className="text-2xl font-bold text-white mb-6">Analytics</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="agency-card p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Leads per client per week</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={d.leads_weekly}>
              <CartesianGrid stroke="#415A77" strokeDasharray="3 3" />
              <XAxis dataKey="week" stroke="#778DA9" />
              <YAxis stroke="#778DA9" />
              <Tooltip contentStyle={{ background: "#1B263B", border: "1px solid #415A77", color: "#E0E1DD" }} />
              <Legend />
              {weekKeys.map((k, i) => <Line key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]} strokeWidth={2} />)}
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="agency-card p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Conversion rate per client</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={d.conversion}>
              <CartesianGrid stroke="#415A77" strokeDasharray="3 3" />
              <XAxis dataKey="name" stroke="#778DA9" />
              <YAxis stroke="#778DA9" />
              <Tooltip contentStyle={{ background: "#1B263B", border: "1px solid #415A77", color: "#E0E1DD" }} />
              <Bar dataKey="conversion" fill="#00B4D8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="agency-card p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Most popular styles</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={d.popular_styles} dataKey="count" nameKey="name" outerRadius={90} label={(x) => x.name}>
                {d.popular_styles.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#1B263B", border: "1px solid #415A77", color: "#E0E1DD" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="agency-card p-5">
          <h3 className="text-sm font-semibold text-white mb-4">Leads by city</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={d.geo}>
              <CartesianGrid stroke="#415A77" strokeDasharray="3 3" />
              <XAxis dataKey="city" stroke="#778DA9" />
              <YAxis stroke="#778DA9" />
              <Tooltip contentStyle={{ background: "#1B263B", border: "1px solid #415A77", color: "#E0E1DD" }} />
              <Bar dataKey="leads" fill="#FFD700" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function StyleIntel() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/agency/style-intel").then((r) => setD(r.data)); }, []);
  if (!d) return <p className="text-[#778DA9]">Loading...</p>;

  return (
    <div data-testid="agency-style-intel-page">
      <h1 className="text-2xl font-bold text-white mb-1">Style Intelligence</h1>
      <p className="text-sm text-[#778DA9] mb-6">Market insights across all clients</p>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <DropOffSection items={d.most_tried_not_booked} />
        <WalkingInSection items={d.walking_in_with} />
        <IntelSection title="Trending this week" items={d.trending} valueKey="count" valueLabel="tried" testid="intel-trending" />
        <GapsSection items={d.market_gaps} />
      </div>
    </div>
  );
}

function DropOffSection({ items }) {
  return (
    <div className="agency-card p-5" data-testid="intel-dropoff">
      <h3 className="text-sm font-semibold text-white mb-1">Most tried but NOT booked</h3>
      <p className="text-xs text-[#778DA9] mb-4">Opportunity gaps — customers want these but aren&apos;t converting</p>
      <div className="space-y-3">
        {(items || []).slice(0, 6).map((it, i) => {
          const dot = it.dropoff_pct >= 60 ? "🔴" : it.dropoff_pct >= 40 ? "🟡" : "🟢";
          return (
            <div key={i} className="flex items-center gap-3">
              <img src={it.image} alt="" className="w-10 h-10 rounded-lg object-cover" />
              <div className="flex-1">
                <p className="text-sm text-white">{it.style_name}</p>
                <p className="text-xs text-[#778DA9]">tried {it.tried}x · booked {it.booked}x</p>
              </div>
              <span className="text-xs text-amber-300">{dot} {it.dropoff_pct}% drop-off</span>
            </div>
          );
        })}
        {(!items || items.length === 0) && <p className="text-xs text-[#778DA9]">Not enough data yet</p>}
      </div>
    </div>
  );
}

function WalkingInSection({ items }) {
  return (
    <div className="agency-card p-5" data-testid="intel-walking-in">
      <h3 className="text-sm font-semibold text-white mb-1">What clients are walking in WITH</h3>
      <p className="text-xs text-[#778DA9] mb-4">Competitor intel — what nails customers already have</p>
      <div className="space-y-3">
        {(items || []).map((it, i) => (
          <div key={i}>
            <div className="flex items-center justify-between text-sm text-white mb-1">
              <span>{it.label}</span>
              <span className="text-[#00B4D8]">{it.pct}%</span>
            </div>
            <div className="h-2 bg-[#0D1B2A] rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-[#00B4D8] to-[#8ED6FB]" style={{ width: `${it.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GapsSection({ items }) {
  return (
    <div className="agency-card p-5" data-testid="intel-gaps">
      <h3 className="text-sm font-semibold text-white mb-1">Market gaps</h3>
      <p className="text-xs text-[#778DA9] mb-4">Styles customers want that no-one offers</p>
      <div className="space-y-3">
        {(items || []).slice(0, 6).map((it, i) => (
          <div key={i} className="flex items-center gap-3">
            <img src={it.image} alt="" className="w-10 h-10 rounded-lg object-cover" />
            <div className="flex-1">
              <p className="text-sm text-white">{it.style_name}</p>
              <p className="text-xs text-[#778DA9]">{it.category}</p>
            </div>
            <span className="text-xs text-[#FFD700]">requested {it.requested}x · {it.tech_count} tech{it.tech_count === 1 ? "" : "s"} offer</span>
          </div>
        ))}
        {(!items || items.length === 0) && <p className="text-xs text-[#778DA9]">No gaps detected</p>}
      </div>
    </div>
  );
}

function IntelSection({ title, items, valueKey, valueLabel, testid }) {
  return (
    <div className="agency-card p-5" data-testid={testid}>
      <h3 className="text-sm font-semibold text-white mb-4">{title}</h3>
      <div className="space-y-3">
        {(items || []).map((it, i) => (
          <div key={i} className="flex items-center gap-3">
            <img src={it.image} alt="" className="w-10 h-10 rounded-lg object-cover" />
            <div className="flex-1">
              <p className="text-sm text-white">{it.style_name}</p>
              {it.category && <p className="text-xs text-[#778DA9]">{it.category}</p>}
            </div>
            {valueKey && <span className="text-xs text-[#00B4D8]">{it[valueKey]} {valueLabel}</span>}
          </div>
        ))}
        {(!items || items.length === 0) && <p className="text-xs text-[#778DA9]">No data yet</p>}
      </div>
    </div>
  );
}

function Billing() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/agency/billing").then((r) => setD(r.data)); }, []);
  if (!d) return <p className="text-[#778DA9]">Loading...</p>;
  return (
    <div data-testid="agency-billing-page">
      <h1 className="text-2xl font-bold text-white mb-1">Billing</h1>
      <p className="text-sm text-[#778DA9] mb-6">MRR and subscriptions</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <KpiCard icon={DollarSign} label="MRR" value={`$${d.mrr}`} accent="#00B4D8" />
        <KpiCard icon={Users} label="Active Subs" value={d.subscriptions.length} accent="#FFD700" />
        <KpiCard icon={TrendingUp} label="Failed Pmts" value={d.failed_payments.length} accent="#C2185B" />
      </div>
      <div className="agency-card p-5 mb-6">
        <h3 className="text-sm font-semibold text-white mb-3">MRR growth</h3>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={d.growth}>
            <CartesianGrid stroke="#415A77" strokeDasharray="3 3" />
            <XAxis dataKey="month" stroke="#778DA9" />
            <YAxis stroke="#778DA9" />
            <Tooltip contentStyle={{ background: "#1B263B", border: "1px solid #415A77", color: "#E0E1DD" }} />
            <Line type="monotone" dataKey="mrr" stroke="#00B4D8" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="agency-card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-xs uppercase tracking-wider text-[#778DA9] text-left">
            <tr className="border-b border-[#415A77]">
              <th className="p-4">Client</th><th className="p-4">Plan</th><th className="p-4">MRR</th><th className="p-4">Status</th><th className="p-4">Renews</th>
            </tr>
          </thead>
          <tbody>
            {d.subscriptions.map((s) => (
              <tr key={s.id} className="border-b border-[#415A77]/50 hover:bg-[#415A77]/20" data-testid={`sub-row-${s.id}`}>
                <td className="p-4 text-white">{s.business_name}</td>
                <td className="p-4 capitalize">{s.plan}</td>
                <td className="p-4">${s.mrr}</td>
                <td className="p-4"><span className="text-xs px-2 py-1 rounded-full bg-green-900/40 text-green-300 border border-green-500/30">{s.status}</span></td>
                <td className="p-4">{s.renewal}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
