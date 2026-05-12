import { Link } from "react-router-dom";
import { Sparkles, ArrowRight } from "lucide-react";

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
              <span className="block">She saw it.</span>
              <span className="block">She tried it on.</span>
              <span className="block italic text-[#C2185B]">She booked it. 💅</span>
            </h1>
            <p className="text-lg text-gray-700 mb-8 leading-relaxed">
              GlowLeads lets clients try your exact nail styles on their own hands before they even DM you. More trust. More bookings. Zero ghosting.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/try/sophie"
                className="funnel-cta pulse-cta inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full text-base"
                data-testid="landing-try-demo-btn"
              >
                See a live demo <ArrowRight className="w-5 h-5" />
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

        <div className="mt-28" data-testid="landing-pricing">
          <div className="text-center mb-12">
            <p className="text-xs uppercase tracking-[0.25em] text-[#C2185B] font-semibold mb-3">Pricing</p>
            <h2 className="font-serif text-4xl md:text-5xl font-bold text-gray-900">Simple plans. Glow-up results.</h2>
            <p className="text-gray-600 mt-3">Cancel anytime · 14-day free trial on every plan</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <PriceCard
              name="Starter"
              price="49"
              testid="pricing-starter"
              features={[
                "AI try-on funnel",
                "Up to 30 styles",
                "Lead capture",
                "Booking calendar",
                "Email support",
              ]}
            />
            <PriceCard
              name="Pro"
              price="99"
              highlighted
              testid="pricing-pro"
              features={[
                "Everything in Starter",
                "Unlimited styles",
                "SMS automations",
                "Lead follow-up sequences",
                "Priority support",
              ]}
            />
            <PriceCard
              name="Agency"
              price="299"
              testid="pricing-agency"
              features={[
                "Everything in Pro",
                "Up to 10 nail tech accounts",
                "Agency dashboard",
                "White label option",
                "Dedicated support",
              ]}
            />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mt-24" data-testid="landing-feature-cards">
          <FeatureCard
            emoji="💅"
            title="AI Try-On"
            copy="Clients see your exact styles on their own hands before booking. More trust, more conversions."
          />
          <FeatureCard
            emoji="📱"
            title="Smart Automations"
            copy="SMS reminders, follow-ups and win-back campaigns running 24/7 while you focus on nails."
          />
          <FeatureCard
            emoji="📊"
            title="Lead Intelligence"
            copy="See every client who tried your funnel with hot and warm lead scoring so you never miss a potential booking."
          />
        </div>
      </main>
    </div>
  );
}

function PriceCard({ name, price, features, highlighted, testid }) {
  return (
    <div
      className={`relative rounded-3xl p-8 border transition shadow-sm hover:shadow-2xl bg-white ${
        highlighted ? "border-[#C2185B] ring-2 ring-[#C2185B]/40" : "border-pink-100"
      }`}
      data-testid={testid}
    >
      {highlighted && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#C2185B] text-white text-[10px] uppercase tracking-[0.2em] font-bold px-3 py-1 rounded-full">
          Most popular
        </span>
      )}
      <p className="text-xs uppercase tracking-[0.2em] text-[#C2185B] font-semibold mb-3">{name}</p>
      <p className="font-serif text-5xl font-bold text-gray-900">
        ${price}
        <span className="text-base font-medium text-gray-500">/month</span>
      </p>
      <ul className="mt-6 space-y-3">
        {features.map((f) => (
          <li key={f} className="flex items-start gap-2 text-sm text-gray-700">
            <span className="text-[#C2185B] mt-0.5">✓</span>
            <span>{f}</span>
          </li>
        ))}
      </ul>
      <Link
        to="/tech/login"
        className={`mt-7 inline-flex w-full items-center justify-center gap-2 px-5 py-3 rounded-full text-sm font-semibold transition ${
          highlighted
            ? "bg-[#C2185B] text-white hover:bg-[#A41450]"
            : "border-2 border-[#C2185B] text-[#C2185B] hover:bg-[#C2185B] hover:text-white"
        }`}
        data-testid={`${testid}-cta`}
      >
        Start {name}
      </Link>
    </div>
  );
}

function FeatureCard({ icon, emoji, title, copy }) {
  return (
    <div className="bg-white/80 backdrop-blur border border-pink-100 rounded-3xl p-6 hover:shadow-xl transition">
      <div className="w-12 h-12 rounded-2xl bg-[#C2185B]/10 text-[#C2185B] flex items-center justify-center mb-4 text-2xl">
        {emoji || icon}
      </div>
      <h3 className="font-serif text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600 leading-relaxed">{copy}</p>
    </div>
  );
}
