import { Link } from "react-router-dom";
import { Sparkles, ArrowRight, Smartphone, BarChart3 } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#fce4ec] via-white to-[#fce4ec]" data-testid="landing-page">
      <header className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-[#C2185B] flex items-center justify-center shadow-lg">
            <Sparkles className="w-5 h-5 text-[#FFD700]" />
          </div>
          <span className="font-serif text-2xl font-bold text-[#C2185B]">GlowLeads</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <Link to="/tech/login" className="text-gray-700 hover:text-[#C2185B]" data-testid="header-tech-login">Nail tech login</Link>
          <Link to="/agency/login" className="text-gray-700 hover:text-[#C2185B]" data-testid="header-agency-login">Agency login</Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="slide-up">
            <p className="text-xs uppercase tracking-[0.25em] text-[#C2185B] font-semibold mb-5">
              AI booking funnel for nail artists
            </p>
            <h1 className="font-serif text-5xl md:text-6xl font-bold leading-[1.05] text-gray-900 mb-6">
              Turn lookers into <span className="italic text-[#C2185B]">bookings</span>.
            </h1>
            <p className="text-lg text-gray-700 mb-8 leading-relaxed">
              GlowLeads lets clients upload a photo of their hands and see your signature styles on their own nails — instantly. The result? More trust, more bookings, fewer ghosted DMs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/try/sophie"
                className="funnel-cta pulse-cta inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full text-base"
                data-testid="landing-try-demo-btn"
              >
                Try the demo funnel <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/tech/login"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full border-2 border-[#C2185B] text-[#C2185B] hover:bg-[#C2185B] hover:text-white transition"
                data-testid="landing-tech-login-btn"
              >
                I&apos;m a nail tech
              </Link>
            </div>
            <p className="mt-4 flex items-center gap-2 text-base font-semibold text-amber-600" data-testid="landing-scarcity">
              <span className="inline-block w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              ⚡ Only 3 spots left this week
            </p>
            <div className="mt-8 text-sm text-gray-600">
              <p>Demo logins:</p>
              <p className="mt-1"><span className="font-semibold">Tech:</span> sophie@glowleads.com / sophie123</p>
              <p><span className="font-semibold">Agency:</span> harry@glowleads.com / agency123</p>
            </div>
          </div>

          <div className="relative slide-up" style={{ animationDelay: "0.1s" }}>
            <img
              src="https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&q=80"
              alt="nail art showcase"
              className="rounded-3xl shadow-2xl w-full h-[500px] object-cover"
            />
            <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl shadow-xl p-5 flex items-center gap-3 max-w-[260px]">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#FFD700] to-[#C2185B] flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-semibold text-sm">AI try-on</p>
                <p className="text-xs text-gray-500">60 signature styles in seconds</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-24">
          <FeatureCard icon={<Sparkles />} title="Customer funnel" copy="7-step premium booking journey with AI try-on and confetti confirmation." />
          <FeatureCard icon={<Smartphone />} title="Tech dashboard" copy="iPhone-simple mobile-first dashboard to manage appointments, leads and styles." />
          <FeatureCard icon={<BarChart3 />} title="Agency console" copy="Multi-tenant SaaS analytics, style intelligence and MRR tracking." />
        </div>
      </main>
    </div>
  );
}

function FeatureCard({ icon, title, copy }) {
  return (
    <div className="bg-white/80 backdrop-blur border border-pink-100 rounded-3xl p-6 hover:shadow-xl transition">
      <div className="w-12 h-12 rounded-2xl bg-[#C2185B]/10 text-[#C2185B] flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="font-serif text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 leading-relaxed">{copy}</p>
    </div>
  );
}
