import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, fileToBase64 } from "@/lib/api";
import { toast } from "sonner";
import {
  Sparkles, Upload, ArrowRight, ArrowLeft, Heart, RotateCcw,
  Calendar as CalendarIcon, Star, Moon, Sun, Loader2, Check, Share2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const CATEGORIES = [
  { key: "FINISHES", label: "Finishes" },
  { key: "FRENCH", label: "French" },
  { key: "OMBRE", label: "Ombre" },
  { key: "NAIL_ART", label: "Nail Art" },
  { key: "EMBELLISHMENTS", label: "Embellishments" },
  { key: "COLORS", label: "Colors" },
  { key: "SPECIALTY", label: "Specialty" },
];

const TIMES = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"];

export default function CustomerFunnel() {
  const { slug } = useParams();
  const [dark, setDark] = useState(false);
  const [step, setStep] = useState(1);
  const [tech, setTech] = useState(null);
  const [styles, setStyles] = useState([]);

  const [imageDataUrl, setImageDataUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const [detection, setDetection] = useState(null);
  const [detecting, setDetecting] = useState(false);

  const [category, setCategory] = useState("FINISHES");
  const [selectedStyle, setSelectedStyle] = useState(null);

  const [generating, setGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  const [form, setForm] = useState({ name: "", phone: "", date: null, time: "" });
  const [leadId, setLeadId] = useState(null);
  const [booked, setBooked] = useState(null);

  useEffect(() => {
    api.get(`/public/tech/${slug}`)
      .then((r) => { setTech(r.data.tech); setStyles(r.data.styles); })
      .catch(() => toast.error("Nail tech not found"));
  }, [slug]);

  const filteredStyles = useMemo(() => {
    let list = styles.filter((s) => s.category === category);
    if (detection?.detected_style_id) list = list.filter((s) => s.id !== detection.detected_style_id);
    return list;
  }, [styles, category, detection]);

  return (
    <div className={`funnel-theme ${dark ? "dark-mode" : ""}`} data-testid="customer-funnel">
      <header className="max-w-6xl mx-auto px-5 py-5 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2" data-testid="funnel-logo">
          <div className="w-9 h-9 rounded-full bg-[#C2185B] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-[#FFD700]" />
          </div>
          <span className="font-serif text-xl font-bold text-[#C2185B]">GlowLeads</span>
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setDark(!dark)}
            className="w-10 h-10 rounded-full border border-[#C2185B]/30 flex items-center justify-center hover:bg-[#C2185B]/10"
            data-testid="funnel-theme-toggle"
          >
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          <StepPill step={step} />
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-5 pb-16">
        {step === 1 && <StepHero tech={tech} onStart={() => setStep(2)} />}
        {step === 2 && (
          <StepUpload
            tech={tech}
            imageDataUrl={imageDataUrl}
            progress={progress}
            uploading={uploading}
            onUpload={async (file) => {
              setUploading(true);
              setProgress(15);
              const dataUrl = await fileToBase64(file);
              setImageDataUrl(dataUrl);
              // fake progress for UX
              let p = 20;
              const iv = setInterval(() => { p = Math.min(100, p + 10); setProgress(p); if (p >= 100) clearInterval(iv); }, 120);
              setTimeout(async () => {
                setUploading(false);
                setStep(3);
                setDetecting(true);
                try {
                  const r = await api.post("/ai/detect", { image_base64: dataUrl });
                  setDetection(r.data);
                } catch { setDetection({ has_polish: false }); }
                finally { setDetecting(false); }
              }, 1300);
            }}
            onBack={() => setStep(1)}
          />
        )}
        {step === 3 && (
          <StepDetect
            detection={detection}
            detecting={detecting}
            onContinue={() => setStep(4)}
          />
        )}
        {step === 4 && (
          <StepSelect
            styles={filteredStyles}
            categories={CATEGORIES}
            category={category}
            onCategory={setCategory}
            onPick={async (s) => {
              setSelectedStyle(s);
              setStep(5);
              setGenerating(true);
              try {
                const r = await api.post("/ai/try-on", { image_base64: imageDataUrl, style_id: s.id, tech_slug: slug });
                setPreviewUrl(r.data.preview);
                // record lead now (without contact info) so agency sees the try-on
                const lead = await api.post("/leads", {
                  tech_slug: slug, name: "Guest", phone: "",
                  style_id: s.id, preview_image: r.data.preview,
                  detected_style_id: detection?.detected_style_id || null,
                });
                setLeadId(lead.data.id);
              } catch (e) {
                toast.error("AI had trouble — showing sample preview");
                setPreviewUrl(s.image);
              } finally { setGenerating(false); }
            }}
            onBack={() => setStep(3)}
          />
        )}
        {step === 5 && (
          <StepResult
            previewUrl={previewUrl}
            style={selectedStyle}
            generating={generating}
            onTryAnother={() => setStep(4)}
            onBook={() => setStep(6)}
          />
        )}
        {step === 6 && (
          <StepBooking
            tech={tech}
            style={selectedStyle}
            previewUrl={previewUrl}
            form={form}
            setForm={setForm}
            onBack={() => setStep(5)}
            onConfirm={async () => {
              if (!form.name || !form.phone || !form.date || !form.time) {
                toast.error("Please fill in all fields"); return;
              }
              try {
                const r = await api.post("/bookings", {
                  tech_slug: slug,
                  name: form.name,
                  phone: form.phone,
                  style_id: selectedStyle.id,
                  date: form.date.toISOString().split("T")[0],
                  time: form.time,
                  preview_image: previewUrl,
                  lead_id: leadId,
                });
                setBooked(r.data.appointment);
                setStep(7);
              } catch (e) {
                toast.error("Could not confirm booking");
              }
            }}
          />
        )}
        {step === 7 && booked && (
          <StepConfirm tech={tech} appointment={booked} previewUrl={previewUrl} />
        )}
      </main>
    </div>
  );
}

function StepPill({ step }) {
  return (
    <div className="text-xs px-3 py-1.5 rounded-full bg-white/70 text-[#C2185B] font-semibold border border-[#C2185B]/20" data-testid="funnel-step-indicator">
      Step {step} of 7
    </div>
  );
}

/* ---------- Step 1: Hero ---------- */
function StepHero({ tech, onStart }) {
  return (
    <section className="grid md:grid-cols-2 gap-10 items-center pt-6 md:pt-12 slide-up">
      <div>
        <p className="uppercase text-xs tracking-[0.25em] text-[#C2185B] font-semibold mb-4">
          {tech ? `with ${tech.business_name}` : "AI nail try-on"}
        </p>
        <h1 className="funnel-headline text-5xl md:text-6xl font-bold leading-[1.03] mb-5">
          See Your Dream<br /><span className="italic text-[#C2185B]">Nails</span> Before You Book
        </h1>
        <p className="text-lg opacity-80 mb-8 max-w-lg">
          Upload a photo of your hands — our AI tries on any style in seconds.
        </p>
        <Button
          onClick={onStart}
          className="funnel-cta pulse-cta rounded-full px-10 py-7 text-lg gap-2 hover:opacity-95"
          data-testid="funnel-hero-cta"
        >
          Try It Free <ArrowRight className="w-5 h-5" />
        </Button>
        <div className="mt-6 flex items-center gap-2 text-sm font-semibold text-[#C2185B]">
          <span className="inline-block w-2 h-2 rounded-full bg-[#FFD700] animate-pulse" />
          3 spots left this week
        </div>
        <div className="mt-10 flex items-center gap-4 text-sm opacity-80">
          <span>2,400+ women transformed</span>
          <span className="flex items-center text-[#FFD700]">
            {[0,1,2,3,4].map((i) => <Star key={i} className="w-4 h-4 fill-current" />)}
          </span>
          <span>Book in 60 seconds</span>
        </div>
      </div>
      <div className="relative">
        <img
          src="https://images.unsplash.com/photo-1604654894610-df63bc536371?w=900&q=85"
          alt=""
          className="w-full h-[520px] object-cover rounded-[2rem] shadow-2xl"
        />
        {tech && (
          <div className="absolute bottom-5 left-5 bg-white/95 rounded-2xl p-4 flex items-center gap-3 shadow-xl">
            <img src={tech.profile_photo} alt={tech.full_name} className="w-12 h-12 rounded-full object-cover" />
            <div>
              <p className="text-sm font-semibold text-gray-900">{tech.full_name}</p>
              <p className="text-xs text-gray-500 flex items-center gap-1">
                <Star className="w-3 h-3 fill-[#FFD700] text-[#FFD700]" /> {tech.rating} · {tech.review_count} reviews
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

/* ---------- Step 2: Upload ---------- */
function StepUpload({ tech, onUpload, onBack, uploading, progress, imageDataUrl }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  return (
    <section className="max-w-2xl mx-auto pt-6 slide-up" data-testid="step-upload">
      <button onClick={onBack} className="mb-4 inline-flex items-center gap-2 text-sm opacity-70 hover:opacity-100">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <h2 className="funnel-headline text-4xl md:text-5xl font-bold mb-3">Upload your hand photo</h2>
      <p className="opacity-80 mb-8">We&apos;ll apply any style onto your real hands in seconds.</p>

      <div
        className={`dropzone rounded-3xl p-10 md:p-14 text-center ${dragging ? "dragging" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault(); setDragging(false);
          const f = e.dataTransfer.files?.[0]; if (f) onUpload(f);
        }}
        onClick={() => inputRef.current?.click()}
        role="button"
        data-testid="upload-dropzone"
      >
        {uploading ? (
          <div>
            <Loader2 className="w-10 h-10 mx-auto text-[#C2185B] animate-spin mb-4" />
            <p className="font-semibold mb-4">Our AI is getting your nails ready... ✨</p>
            <div className="h-2 bg-white rounded-full overflow-hidden max-w-xs mx-auto">
              <div className="h-full bg-gradient-to-r from-[#C2185B] to-[#FFD700] transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
        ) : imageDataUrl ? (
          <img src={imageDataUrl} alt="" className="max-h-64 mx-auto rounded-2xl" />
        ) : (
          <div>
            <div className="w-16 h-16 rounded-full bg-[#C2185B]/10 text-[#C2185B] mx-auto flex items-center justify-center mb-4">
              <Upload className="w-7 h-7" />
            </div>
            <p className="font-serif text-2xl mb-2">Drop your hand photo here</p>
            <p className="text-sm opacity-70">or tap to upload</p>
          </div>
        )}
        <input
          ref={inputRef} type="file" accept="image/*" className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) onUpload(f); }}
          data-testid="upload-file-input"
        />
      </div>
      <p className="text-xs opacity-60 mt-4 text-center">🔒 Your photo is private and deleted after your session</p>
    </section>
  );
}

/* ---------- Step 3: Detect ---------- */
function StepDetect({ detection, detecting, onContinue }) {
  useEffect(() => {
    if (!detecting && detection) {
      const t = setTimeout(onContinue, 1800);
      return () => clearTimeout(t);
    }
  }, [detecting, detection, onContinue]);

  return (
    <section className="max-w-2xl mx-auto pt-16 text-center slide-up" data-testid="step-detect">
      {detecting ? (
        <>
          <Loader2 className="w-10 h-10 mx-auto text-[#C2185B] animate-spin mb-4" />
          <h2 className="funnel-headline text-3xl mb-2">Reading your nails...</h2>
          <p className="opacity-70">Our AI is analyzing your current style ✨</p>
        </>
      ) : detection?.detected_style_name ? (
        <>
          <div className="w-16 h-16 rounded-full bg-[#FFD700]/30 mx-auto flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-[#C2185B]" />
          </div>
          <h2 className="funnel-headline text-3xl mb-3">
            We noticed you&apos;re rocking <span className="italic text-[#C2185B]">{detection.detected_style_name}</span>!
          </h2>
          <p className="opacity-75">Here are some fresh new looks for you 💅</p>
        </>
      ) : (
        <>
          <div className="w-16 h-16 rounded-full bg-[#FFD700]/30 mx-auto flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-[#C2185B]" />
          </div>
          <h2 className="funnel-headline text-3xl mb-3">Try something totally new ✨</h2>
          <p className="opacity-75">Our full style library is ready for you.</p>
        </>
      )}
    </section>
  );
}

/* ---------- Step 4: Select Style ---------- */
function StepSelect({ styles, categories, category, onCategory, onPick, onBack }) {
  return (
    <section className="pt-4 slide-up" data-testid="step-select">
      <div className="flex items-center justify-between mb-5">
        <div>
          <button onClick={onBack} className="mb-2 text-sm opacity-70 inline-flex items-center gap-2"><ArrowLeft className="w-4 h-4" /> Back</button>
          <h2 className="funnel-headline text-3xl md:text-4xl font-bold">Which look are you feeling today?</h2>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2 mb-6">
        {categories.map((c) => (
          <button
            key={c.key}
            onClick={() => onCategory(c.key)}
            className={`shrink-0 px-5 py-2 rounded-full text-sm font-semibold uppercase tracking-wider border transition ${
              category === c.key
                ? "bg-[#C2185B] text-white border-[#C2185B]"
                : "bg-white/70 text-[#C2185B] border-[#C2185B]/30 hover:bg-white"
            }`}
            data-testid={`category-tab-${c.key}`}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
        {styles.map((s) => (
          <button
            key={s.id}
            onClick={() => onPick(s)}
            className="group text-left bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl hover:ring-2 hover:ring-[#FFD700] transition"
            data-testid={`style-card-${s.id}`}
          >
            <div className="aspect-square overflow-hidden">
              <img src={s.image} alt={s.name} className="w-full h-full object-cover group-hover:scale-105 transition" />
            </div>
            <div className="p-4">
              <h3 className="font-serif text-lg font-semibold text-gray-900 leading-tight">{s.name}</h3>
              <p className="text-xs text-gray-500 mt-1">{s.description}</p>
              <p className="text-xs text-[#C2185B] font-semibold mt-2">${s.price_range.low}–${s.price_range.high}</p>
            </div>
          </button>
        ))}
        {styles.length === 0 && (
          <p className="col-span-full text-center opacity-60 py-10">No styles in this category yet.</p>
        )}
      </div>
    </section>
  );
}

/* ---------- Step 5: Result ---------- */
function StepResult({ previewUrl, style, generating, onTryAnother, onBook }) {
  const dayName = new Date(Date.now() + 86400000 * 3).toLocaleDateString("en-US", { weekday: "long" });
  return (
    <section className="max-w-3xl mx-auto pt-4 slide-up" data-testid="step-result">
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold text-center mb-6">
        This could be you on {dayName} ✨
      </h2>
      <div className="relative rounded-[2rem] overflow-hidden shadow-2xl bg-white">
        {generating ? (
          <div className="aspect-[4/3] flex flex-col items-center justify-center p-10 bg-gradient-to-br from-[#fce4ec] to-white">
            <Loader2 className="w-10 h-10 text-[#C2185B] animate-spin mb-4" />
            <p className="font-serif text-xl">Applying {style?.name}...</p>
            <p className="text-sm opacity-70 mt-1">This usually takes 10–20 seconds</p>
          </div>
        ) : (
          <img src={previewUrl} alt="preview" className="w-full shimmer-reveal" data-testid="result-preview-image" />
        )}
      </div>
      {!generating && (
        <div className="grid grid-cols-3 gap-3 mt-6">
          <Button variant="outline" className="rounded-full py-6 border-[#C2185B]/30" data-testid="result-love-btn">
            <Heart className="w-4 h-4 mr-2 text-[#C2185B]" /> Love it
          </Button>
          <Button variant="outline" onClick={onTryAnother} className="rounded-full py-6 border-[#C2185B]/30" data-testid="result-retry-btn">
            <RotateCcw className="w-4 h-4 mr-2" /> Try another
          </Button>
          <Button onClick={onBook} className="funnel-cta pulse-cta rounded-full py-6" data-testid="result-book-btn">
            <CalendarIcon className="w-4 h-4 mr-2" /> Book this look
          </Button>
        </div>
      )}
    </section>
  );
}

/* ---------- Step 6: Booking ---------- */
function StepBooking({ tech, style, previewUrl, form, setForm, onConfirm, onBack }) {
  return (
    <section className="max-w-2xl mx-auto pt-4 slide-up" data-testid="step-booking">
      <button onClick={onBack} className="mb-3 text-sm opacity-70 inline-flex items-center gap-2">
        <ArrowLeft className="w-4 h-4" /> Back to preview
      </button>
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold mb-6">Confirm your appointment</h2>

      <div className="bg-white rounded-3xl p-6 shadow-lg mb-6 flex items-center gap-4">
        <img src={previewUrl || style?.image} alt="" className="w-24 h-24 rounded-2xl object-cover" />
        <div className="flex-1">
          <p className="text-xs uppercase tracking-wider text-[#C2185B] font-semibold">Your pick</p>
          <p className="font-serif text-xl font-semibold text-gray-900">{style?.name}</p>
          <p className="text-sm text-gray-500">${style?.price_range.low}–${style?.price_range.high}</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 shadow-lg space-y-4">
        <div>
          <Label htmlFor="name">Your name</Label>
          <Input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Jane Doe" className="mt-1" data-testid="booking-name-input" />
        </div>
        <div>
          <Label htmlFor="phone">Phone number</Label>
          <Input id="phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+1 415 555 0199" className="mt-1" data-testid="booking-phone-input" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-start mt-1" data-testid="booking-date-trigger">
                  <CalendarIcon className="w-4 h-4 mr-2" />
                  {form.date ? form.date.toLocaleDateString() : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={form.date}
                  onSelect={(d) => setForm({ ...form, date: d })}
                  disabled={(d) => d < new Date(new Date().setHours(0,0,0,0))}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
          <div>
            <Label>Time</Label>
            <Select value={form.time} onValueChange={(v) => setForm({ ...form, time: v })}>
              <SelectTrigger className="mt-1" data-testid="booking-time-select"><SelectValue placeholder="Select time" /></SelectTrigger>
              <SelectContent>
                {TIMES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button onClick={onConfirm} className="funnel-cta pulse-cta w-full rounded-full py-7 text-base" data-testid="booking-confirm-btn">
          Confirm My Appointment <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
        <p className="text-xs text-center opacity-70">✅ You&apos;ll get an SMS confirmation instantly</p>
      </div>

      {tech && (
        <div className="flex items-center gap-3 mt-6 bg-white/70 rounded-2xl p-4">
          <img src={tech.profile_photo} alt="" className="w-11 h-11 rounded-full object-cover" />
          <div className="flex-1">
            <p className="text-sm font-semibold">{tech.full_name}</p>
            <p className="text-xs opacity-70">Certified Nail Artist · ⭐ {tech.rating}</p>
          </div>
        </div>
      )}
    </section>
  );
}

/* ---------- Step 7: Confirm ---------- */
function StepConfirm({ tech, appointment, previewUrl }) {
  return (
    <section className="relative max-w-2xl mx-auto pt-8 text-center slide-up" data-testid="step-confirm">
      <Confetti />
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#FFD700] to-[#C2185B] mx-auto flex items-center justify-center mb-5 shadow-xl">
        <Check className="w-10 h-10 text-white" strokeWidth={3} />
      </div>
      <h2 className="funnel-headline text-4xl md:text-5xl font-bold mb-3">You&apos;re booked! 🎉</h2>
      <p className="text-lg opacity-80 mb-8">{tech?.full_name} can&apos;t wait to see you</p>

      <div className="bg-white rounded-3xl p-6 shadow-xl text-left max-w-md mx-auto">
        <img src={previewUrl} alt="" className="w-full rounded-2xl mb-4" />
        <div className="space-y-2 text-sm">
          <Row label="Style" value={appointment.style_name} />
          <Row label="Date" value={appointment.date} />
          <Row label="Time" value={appointment.time} />
          <Row label="With" value={tech?.business_name} />
          <Row label="Price" value={`$${appointment.price}`} />
        </div>
        <div className="grid grid-cols-2 gap-3 mt-5">
          <Button variant="outline" className="rounded-full" data-testid="confirm-calendar-btn">
            <CalendarIcon className="w-4 h-4 mr-2" /> Add to calendar
          </Button>
          <Button className="funnel-cta rounded-full" data-testid="confirm-share-btn">
            <Share2 className="w-4 h-4 mr-2" /> Share preview
          </Button>
        </div>
      </div>
    </section>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="opacity-60">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

function Confetti() {
  const pieces = useMemo(() => Array.from({ length: 60 }, () => ({
    left: `${Math.random() * 100}%`,
    delay: `${Math.random() * 1.2}s`,
    color: ["#FFD700", "#C2185B", "#FCE4EC", "#FFB3C1", "#FFFFFF"][Math.floor(Math.random() * 5)],
    rotate: `${Math.random() * 360}deg`,
  })), []);
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden z-50">
      {pieces.map((p, i) => (
        <span
          key={i} className="confetti-piece"
          style={{ left: p.left, animationDelay: p.delay, background: p.color, transform: `rotate(${p.rotate})` }}
        />
      ))}
    </div>
  );
}
