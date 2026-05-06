import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, fileToBase64 } from "@/lib/api";
import { toast } from "sonner";
import {
  Sparkles, Upload, ArrowRight, ArrowLeft, Heart, RotateCcw,
  Calendar as CalendarIcon, Star, Loader2, Check, Share2,
  X, Palette, Hand,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";

const TIMES = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"];

export default function CustomerFunnel() {
  const { slug } = useParams();
  const [step, setStep] = useState(1);
  const [tech, setTech] = useState(null);
  const [config, setConfig] = useState(null);

  // Persistent session state — never re-uploaded
  const [imageDataUrl, setImageDataUrl] = useState(null);
  const [detection, setDetection] = useState(null);
  const [detecting, setDetecting] = useState(false);

  const [shape, setShape] = useState(null);
  const [design, setDesign] = useState(null);
  const [color, setColor] = useState(null);

  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState("");
  const [previewUrl, setPreviewUrl] = useState(null);
  const [leadId, setLeadId] = useState(null);

  // Bottom-sheet UIs for changing pieces post-result
  const [sheet, setSheet] = useState(null); // 'shape' | 'design' | 'color' | null

  // Booking
  const [bookingOpen, setBookingOpen] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", email: "", date: null, time: "", notes: "" });
  const [booked, setBooked] = useState(null);

  useEffect(() => {
    api.get(`/public/tech/${slug}`).then((r) => setTech(r.data.tech)).catch(() => toast.error("Nail tech not found"));
    api.get("/funnel/config").then((r) => setConfig(r.data));
  }, [slug]);

  const generate = async (overrides = {}) => {
    const useShape = overrides.shape || shape;
    const useDesign = overrides.design || design;
    const useColor = overrides.color || color;
    if (!useDesign) { toast.error("Pick a design first"); return; }
    setGenerating(true);
    setProgress(0);
    setStep(5);
    const messages = [
      "Analyzing your hand...",
      `Applying ${useDesign.label}...`,
      `Adding ${useColor?.name || "your colour"}...`,
      "Almost ready...",
    ];
    let mIdx = 0;
    setProgressMsg(messages[0]);
    const iv = setInterval(() => {
      setProgress((p) => Math.min(p + 4, 95));
      mIdx = Math.min(mIdx + 1, messages.length - 1);
      setProgressMsg(messages[mIdx]);
    }, 800);
    try {
      const r = await api.post("/ai/try-on", {
        image_base64: imageDataUrl,
        tech_slug: slug,
        design_id: useDesign.id,
        shape_id: useShape?.id,
        color_hex: useColor?.hex,
        color_name: useColor?.name,
      });
      setPreviewUrl(r.data.preview);
      // Record lead with full context
      if (!leadId) {
        const lead = await api.post("/leads", {
          tech_slug: slug,
          name: "Guest",
          phone: "",
          design_id: useDesign.id,
          shape_id: useShape?.id,
          preview_image: r.data.preview,
          color_hex: useColor?.hex,
          color_name: useColor?.name,
        });
        setLeadId(lead.data.id);
      }
    } catch {
      toast.error("AI hiccup — showing reference image");
      setPreviewUrl(useDesign.image);
    } finally {
      clearInterval(iv);
      setProgress(100);
      setProgressMsg("Done ✨");
      setGenerating(false);
    }
  };

  if (!config) {
    return <div className="funnel-theme min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-[#C2185B]" /></div>;
  }

  return (
    <div className="funnel-theme" data-testid="customer-funnel">
      <header className="max-w-6xl mx-auto px-5 py-5 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2" data-testid="funnel-logo">
          <div className="w-9 h-9 rounded-full bg-[#C2185B] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-[#FFD700]" />
          </div>
          <span className="font-serif text-xl font-bold text-[#C2185B]">GlowLeads</span>
        </Link>
        <div className="text-xs px-3 py-1.5 rounded-full bg-white/70 text-[#C2185B] font-semibold border border-[#C2185B]/20" data-testid="funnel-step-indicator">
          Step {step} of 6
        </div>
      </header>

      {/* Selection chips bar */}
      {(shape || design || color) && step > 1 && (
        <div className="max-w-6xl mx-auto px-5 mb-3 flex flex-wrap gap-2 text-xs">
          {shape && <Chip icon="✋" label={shape.label} onClear={() => setShape(null)} />}
          {design && <Chip icon="💅" label={design.label} onClear={() => setDesign(null)} />}
          {color && <Chip icon={<span className="w-3 h-3 rounded-full inline-block" style={{ background: color.hex }} />} label={color.name} onClear={() => setColor(null)} />}
        </div>
      )}

      <main className="max-w-6xl mx-auto px-5 pb-32">
        {step === 1 && <StepUpload
          tech={tech}
          imageDataUrl={imageDataUrl}
          detecting={detecting}
          detection={detection}
          onUpload={async (file) => {
            const dataUrl = await fileToBase64(file);
            setImageDataUrl(dataUrl);
            setDetecting(true);
            try {
              const r = await api.post("/ai/detect-shape", { image_base64: dataUrl });
              setDetection(r.data);
              if (r.data.shape_id && config) {
                const matched = config.shapes.find((s) => s.id === r.data.shape_id);
                if (matched) setShape(matched);
              }
            } catch {} finally { setDetecting(false); }
            setTimeout(() => setStep(2), 1800);
          }}
        />}
        {step === 2 && <StepShape
          shapes={config.shapes}
          detected={detection?.shape_id}
          selected={shape?.id}
          onPick={(s) => { setShape(s); setStep(3); }}
        />}
        {step === 3 && <StepDesign
          groups={config.design_groups}
          selected={design?.id}
          onPick={(d) => { setDesign(d); setStep(4); }}
          onBack={() => setStep(2)}
        />}
        {step === 4 && <StepColor
          groups={config.color_groups}
          selected={color}
          onSelect={setColor}
          onBack={() => setStep(3)}
          onApply={() => generate()}
        />}
        {step === 5 && <StepResult
          tech={tech}
          imageDataUrl={imageDataUrl}
          previewUrl={previewUrl}
          generating={generating}
          progress={progress}
          progressMsg={progressMsg}
          shape={shape}
          design={design}
          color={color}
          onChangeColor={() => setSheet("color")}
          onChangeDesign={() => setSheet("design")}
          onChangeShape={() => setSheet("shape")}
          onBook={() => setBookingOpen(true)}
        />}
      </main>

      {/* Bottom sheets for change-without-restart */}
      <Sheet open={sheet === "color"} onOpenChange={(o) => !o && setSheet(null)}>
        <SheetContent side="bottom" className="h-[80vh] overflow-y-auto rounded-t-3xl">
          <SheetHeader><SheetTitle>Change colour</SheetTitle></SheetHeader>
          <ColorPalette
            groups={config.color_groups}
            selected={color}
            onSelect={(c) => {
              setColor(c);
              setSheet(null);
              generate({ color: c });
            }}
          />
        </SheetContent>
      </Sheet>

      <Sheet open={sheet === "design"} onOpenChange={(o) => !o && setSheet(null)}>
        <SheetContent side="bottom" className="h-[85vh] overflow-y-auto rounded-t-3xl">
          <SheetHeader><SheetTitle>Change design</SheetTitle></SheetHeader>
          <DesignGrid
            groups={config.design_groups}
            selected={design?.id}
            onPick={(d) => {
              setSheet(null);
              const keepColor = window.confirm(`Keep ${color?.name || "current colour"}?`);
              setDesign(d);
              if (!keepColor) { setColor(null); setStep(4); return; }
              generate({ design: d });
            }}
          />
        </SheetContent>
      </Sheet>

      <Sheet open={sheet === "shape"} onOpenChange={(o) => !o && setSheet(null)}>
        <SheetContent side="bottom" className="h-[80vh] overflow-y-auto rounded-t-3xl">
          <SheetHeader><SheetTitle>Change shape</SheetTitle></SheetHeader>
          <ShapeGrid
            shapes={config.shapes}
            detected={detection?.shape_id}
            selected={shape?.id}
            onPick={(s) => {
              setSheet(null);
              setShape(s);
              const keep = window.confirm(`Keep ${design?.label} + ${color?.name || "colour"}?`);
              if (!keep) { setDesign(null); setColor(null); setStep(3); return; }
              generate({ shape: s });
            }}
          />
        </SheetContent>
      </Sheet>

      {/* Booking sheet */}
      <Sheet open={bookingOpen} onOpenChange={setBookingOpen}>
        <SheetContent side="bottom" className="h-[90vh] overflow-y-auto rounded-t-3xl">
          {!booked ? (
            <BookingForm
              tech={tech}
              shape={shape} design={design} color={color}
              previewUrl={previewUrl}
              form={form} setForm={setForm}
              onSubmit={async () => {
                if (!form.name || !form.phone || !form.date || !form.time) {
                  toast.error("Please fill in name, phone, date and time"); return;
                }
                try {
                  const r = await api.post("/bookings", {
                    tech_slug: slug,
                    name: form.name,
                    phone: form.phone,
                    email: form.email,
                    design_id: design.id,
                    shape_id: shape?.id,
                    color_hex: color?.hex,
                    color_name: color?.name,
                    color_brand: color?.brand,
                    notes: form.notes,
                    date: form.date.toISOString().split("T")[0],
                    time: form.time,
                    preview_image: previewUrl,
                    lead_id: leadId,
                  });
                  setBooked(r.data.appointment);
                } catch (e) { toast.error("Could not confirm booking"); }
              }}
            />
          ) : (
            <BookingConfirm tech={tech} appointment={booked} previewUrl={previewUrl} design={design} color={color} />
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

/* ---------- helpers / sub-components ---------- */

function Chip({ icon, label, onClear }) {
  return (
    <span className="bg-white rounded-full px-3 py-1.5 shadow-sm border border-[#C2185B]/20 flex items-center gap-1.5 text-[#C2185B] font-semibold">
      <span>{icon}</span>
      <span>{label}</span>
      {onClear && (
        <button onClick={onClear} className="opacity-50 hover:opacity-100"><X className="w-3 h-3" /></button>
      )}
    </span>
  );
}

/* ---------- Step 1: Upload + auto-detect ---------- */
function StepUpload({ tech, imageDataUrl, onUpload, detecting, detection }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  return (
    <section className="max-w-2xl mx-auto pt-4 slide-up" data-testid="step-upload">
      <h1 className="funnel-headline text-4xl md:text-5xl font-bold mb-3 text-center">
        See any nail style on <span className="italic text-[#C2185B]">YOUR</span> hands
      </h1>
      <p className="opacity-70 text-center mb-8">Upload a clear photo of your hand. We&apos;ll do the rest.</p>

      {!imageDataUrl ? (
        <div
          className={`dropzone rounded-3xl p-12 md:p-16 text-center cursor-pointer ${dragging ? "dragging" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files?.[0]; if (f) onUpload(f); }}
          onClick={() => inputRef.current?.click()}
          data-testid="upload-dropzone"
        >
          <div className="w-16 h-16 rounded-full bg-[#C2185B]/10 text-[#C2185B] mx-auto flex items-center justify-center mb-4">
            <Upload className="w-7 h-7" />
          </div>
          <p className="font-serif text-2xl mb-2">Drop your hand photo here</p>
          <p className="text-sm opacity-70">or tap to upload • JPG / PNG</p>
          <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/jpg" className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onUpload(f); }} data-testid="upload-file-input" />
        </div>
      ) : (
        <div className="text-center">
          <div className="relative w-44 h-44 mx-auto mb-6">
            <img src={imageDataUrl} alt="" className="w-44 h-44 rounded-full object-cover ring-4 ring-[#FFD700] shadow-2xl" />
            {detecting && <div className="absolute inset-0 rounded-full bg-black/30 flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>}
          </div>
          {detecting && <p className="font-serif text-xl">Reading your nails... 3–5 sec</p>}
          {!detecting && detection && (
            <p className="font-serif text-xl text-[#C2185B]">
              We detected: <span className="italic">{detection.shape_label || "your shape"}</span> {detection.length} nails — let&apos;s transform them ✨
            </p>
          )}
        </div>
      )}
      <p className="text-xs opacity-60 mt-6 text-center">🔒 Your photo is private and deleted after your session</p>
    </section>
  );
}

/* ---------- Step 2: Pick shape ---------- */
function StepShape({ shapes, detected, selected, onPick }) {
  return (
    <section className="slide-up" data-testid="step-shape">
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold mb-1 text-center">Choose your nail shape</h2>
      <p className="text-sm opacity-70 text-center mb-6">This is the foundation of your look</p>
      <ShapeGrid shapes={shapes} detected={detected} selected={selected} onPick={onPick} />
    </section>
  );
}

function ShapeGrid({ shapes, detected, selected, onPick }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {shapes.map((s) => (
        <button
          key={s.id}
          onClick={() => onPick(s)}
          className={`group text-left bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl transition relative ${
            selected === s.id ? "ring-4 ring-[#FFD700]" : ""
          }`}
          data-testid={`shape-card-${s.id}`}
        >
          {detected === s.id && (
            <span className="absolute top-3 right-3 z-10 bg-[#C2185B] text-white text-[10px] uppercase tracking-wider font-semibold px-2 py-1 rounded-full">
              Detected
            </span>
          )}
          <div className="aspect-[4/3] overflow-hidden">
            <img src={s.image} alt={s.label} className="w-full h-full object-cover group-hover:scale-105 transition" loading="lazy" />
          </div>
          <div className="p-4">
            <h3 className="font-serif text-xl font-semibold">{s.label}</h3>
            <p className="text-xs text-gray-500">{s.description}</p>
          </div>
        </button>
      ))}
    </div>
  );
}

/* ---------- Step 3: Pick design ---------- */
function StepDesign({ groups, selected, onPick, onBack }) {
  const [active, setActive] = useState(groups[0]?.id);
  return (
    <section className="slide-up" data-testid="step-design">
      <button onClick={onBack} className="mb-3 text-sm opacity-70 inline-flex items-center gap-2"><ArrowLeft className="w-4 h-4" /> Back</button>
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold mb-1">Choose your design</h2>
      <p className="text-sm opacity-70 mb-5">Pick the style that speaks to you</p>
      <div className="flex gap-2 overflow-x-auto no-scrollbar pb-2 mb-5">
        {groups.map((g) => (
          <button
            key={g.id}
            onClick={() => setActive(g.id)}
            className={`shrink-0 px-4 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider border transition ${
              active === g.id ? "bg-[#C2185B] text-white border-[#C2185B]" : "bg-white text-[#C2185B] border-[#C2185B]/30"
            }`}
            data-testid={`design-cat-${g.id}`}
          >
            {g.label}
          </button>
        ))}
      </div>
      <DesignGrid groups={groups} active={active} selected={selected} onPick={onPick} />
    </section>
  );
}

function DesignGrid({ groups, active, selected, onPick }) {
  const list = active ? (groups.find((g) => g.id === active)?.designs || []) : groups.flatMap((g) => g.designs);
  return (
    <div className="grid grid-cols-2 gap-4">
      {list.map((d) => (
        <button
          key={d.id}
          onClick={() => onPick(d)}
          className={`group text-left bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl transition relative ${
            selected === d.id ? "ring-4 ring-[#FFD700]" : ""
          }`}
          data-testid={`design-card-${d.id}`}
        >
          {d.badge && (
            <span className="absolute top-3 left-3 z-10 bg-[#FFD700] text-[#1f2937] text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-full">
              {d.badge}
            </span>
          )}
          <div className="aspect-square overflow-hidden">
            <img src={d.image} alt={d.label} className="w-full h-full object-cover group-hover:scale-105 transition" loading="lazy" />
          </div>
          <div className="p-3">
            <h3 className="font-serif text-base font-semibold">{d.label}</h3>
            <p className="text-xs text-[#C2185B] font-semibold">${d.price_range.low}–${d.price_range.high}</p>
          </div>
        </button>
      ))}
    </div>
  );
}

/* ---------- Step 4: Pick colour ---------- */
function StepColor({ groups, selected, onSelect, onBack, onApply }) {
  return (
    <section className="slide-up pb-28" data-testid="step-color">
      <button onClick={onBack} className="mb-3 text-sm opacity-70 inline-flex items-center gap-2"><ArrowLeft className="w-4 h-4" /> Back</button>
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold mb-1">Choose your colour</h2>
      <p className="text-sm opacity-70 mb-6">Tap any shade to see it on your nails</p>
      <ColorPalette groups={groups} selected={selected} onSelect={onSelect} />

      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur border-t border-[#C2185B]/10 px-5 py-3 z-30 shadow-2xl" data-testid="color-bottom-bar">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="w-9 h-9 rounded-full border-2 border-[#FFD700] shrink-0" style={{ background: selected?.hex || "#fff" }} />
            <div className="min-w-0">
              <p className="text-sm font-semibold truncate">{selected?.name || "Pick a colour"}</p>
              <p className="text-[11px] text-gray-500 truncate">{selected?.brand || "—"}</p>
            </div>
          </div>
          <Button
            disabled={!selected}
            className="funnel-cta rounded-full px-6 py-5"
            onClick={onApply}
            data-testid="color-apply-btn"
          >
            Apply <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </section>
  );
}

function ColorPalette({ groups, selected, onSelect }) {
  return (
    <div className="space-y-7">
      {groups.map((g) => (
        <div key={g.id}>
          <h3 className="text-xs uppercase tracking-[0.2em] font-semibold text-[#C2185B] mb-3" data-testid={`color-group-${g.id}`}>
            ━━━ {g.label} ━━━
          </h3>
          <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2 pl-1">
            {g.colors.map((c, i) => {
              const sel = selected?.hex === c.hex && selected?.name === c.name;
              return (
                <button
                  key={`${c.hex}-${i}`}
                  onClick={() => onSelect(c)}
                  className={`shrink-0 w-12 h-12 rounded-full transition flex items-center justify-center relative ${
                    sel ? "ring-[3px] ring-[#FFD700] scale-110" : "ring-1 ring-black/10 hover:scale-105"
                  }`}
                  style={{ background: c.hex }}
                  title={`${c.name} — ${c.brand}`}
                  data-testid={`color-swatch-${c.hex.replace("#", "")}`}
                >
                  {sel && <Check className="w-4 h-4 text-white drop-shadow" strokeWidth={3} />}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---------- Step 5: Result + change actions ---------- */
function StepResult({ tech, imageDataUrl, previewUrl, generating, progress, progressMsg, shape, design, color, onChangeColor, onChangeDesign, onChangeShape, onBook }) {
  const dayName = new Date(Date.now() + 86400000 * 3).toLocaleDateString("en-US", { weekday: "long" });
  return (
    <section className="max-w-3xl mx-auto pt-2 slide-up pb-32" data-testid="step-result">
      <h2 className="funnel-headline text-3xl md:text-4xl font-bold text-center mb-4">
        This could be you on {dayName} ✨
      </h2>

      <div className="relative rounded-[2rem] overflow-hidden shadow-2xl bg-white">
        {generating ? (
          <div className="relative aspect-[4/3]">
            {imageDataUrl && <img src={imageDataUrl} alt="" className="absolute inset-0 w-full h-full object-cover opacity-40 blur-sm" />}
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 bg-gradient-to-br from-[#fce4ec]/60 to-white/40">
              <Loader2 className="w-10 h-10 text-[#C2185B] animate-spin mb-4" />
              <p className="font-serif text-xl mb-3">{progressMsg}</p>
              <div className="w-full max-w-xs h-2 bg-white/80 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-[#C2185B] to-[#FFD700] transition-all" style={{ width: `${progress}%` }} />
              </div>
            </div>
          </div>
        ) : (
          <img src={previewUrl} alt="" className="w-full shimmer-reveal" data-testid="result-preview-image" />
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 mt-6">
        <Button variant="outline" onClick={onChangeColor} className="rounded-full py-6 border-[#C2185B]/30" disabled={generating} data-testid="change-color-btn">
          🎨 Colour
        </Button>
        <Button variant="outline" onClick={onChangeDesign} className="rounded-full py-6 border-[#C2185B]/30" disabled={generating} data-testid="change-design-btn">
          💅 Design
        </Button>
        <Button variant="outline" onClick={onChangeShape} className="rounded-full py-6 border-[#C2185B]/30" disabled={generating} data-testid="change-shape-btn">
          ✋ Shape
        </Button>
      </div>

      <Button onClick={onBook} disabled={generating} className="funnel-cta pulse-cta w-full rounded-full py-7 text-base mt-3" data-testid="book-now-btn">
        <Heart className="w-5 h-5 mr-2 text-[#C2185B] fill-[#C2185B]" /> Love it? Book Now
      </Button>
    </section>
  );
}

/* ---------- Booking ---------- */
function BookingForm({ tech, shape, design, color, previewUrl, form, setForm, onSubmit }) {
  return (
    <div className="pt-2" data-testid="booking-form">
      <h2 className="font-serif text-2xl font-bold mb-2">Confirm your appointment</h2>
      <div className="bg-[#fce4ec]/40 rounded-2xl p-4 mb-4 flex items-center gap-3">
        {previewUrl && <img src={previewUrl} alt="" className="w-16 h-16 rounded-xl object-cover" />}
        <div className="flex-1 min-w-0">
          <p className="text-xs opacity-60">Your selection</p>
          <p className="font-semibold text-sm truncate">
            {[shape?.label, design?.label, color?.name].filter(Boolean).join(" · ")}
          </p>
          {color && <p className="text-[11px] opacity-60">{color.brand}</p>}
        </div>
      </div>
      <div className="space-y-3">
        <div>
          <Label>Name</Label>
          <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Jane Doe" data-testid="booking-name-input" />
        </div>
        <div>
          <Label>Phone</Label>
          <Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+1 403 555 0199" data-testid="booking-phone-input" />
        </div>
        <div>
          <Label>Email</Label>
          <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="jane@example.com" data-testid="booking-email-input" />
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
                <Calendar mode="single" selected={form.date} onSelect={(d) => setForm({ ...form, date: d })}
                  disabled={(d) => d < new Date(new Date().setHours(0, 0, 0, 0))} initialFocus />
              </PopoverContent>
            </Popover>
          </div>
          <div>
            <Label>Time</Label>
            <Select value={form.time} onValueChange={(v) => setForm({ ...form, time: v })}>
              <SelectTrigger className="mt-1" data-testid="booking-time-select"><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent>
                {TIMES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div>
          <Label>Notes (optional)</Label>
          <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} rows={2} placeholder="Any preferences or details..." data-testid="booking-notes-input" />
        </div>
        <Button onClick={onSubmit} className="funnel-cta w-full rounded-full py-7 text-base" data-testid="booking-submit-btn">
          Confirm My Appointment <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}

function BookingConfirm({ tech, appointment, previewUrl, design, color }) {
  return (
    <div className="text-center pt-4" data-testid="booking-confirm">
      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#FFD700] to-[#C2185B] mx-auto flex items-center justify-center mb-4 shadow-xl">
        <Check className="w-10 h-10 text-white" strokeWidth={3} />
      </div>
      <h2 className="font-serif text-3xl font-bold mb-2">You&apos;re booked! ✨</h2>
      <p className="text-sm opacity-80 mb-6">
        {tech?.business_name} is preparing<br />
        <span className="font-semibold">{design?.label}</span>{color && <> in <span className="font-semibold">{color.name}</span></>}
        <br /> See you {appointment.date} at {appointment.time}!
      </p>
      {previewUrl && <img src={previewUrl} alt="" className="w-full max-w-xs mx-auto rounded-2xl shadow-lg mb-4" />}
      <Confetti />
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
        <span key={i} className="confetti-piece"
          style={{ left: p.left, animationDelay: p.delay, background: p.color, transform: `rotate(${p.rotate})` }} />
      ))}
    </div>
  );
}
