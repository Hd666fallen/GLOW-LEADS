// Fallback image shown when an Unsplash URL fails.
// Uses an inline SVG data URL — always available, no network call.
const FALLBACKS = {
  FINISHES: "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600&q=80",
  FRENCH: "https://images.unsplash.com/photo-1519419691348-3b3433c4c20e?w=600&q=80",
  OMBRE: "https://images.unsplash.com/photo-1607779097040-26e80aa78e66?w=600&q=80",
  NAIL_ART: "https://images.unsplash.com/photo-1604654894710-3c7d74bfdb1e?w=600&q=80",
  EMBELLISHMENTS: "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=600&q=80",
  COLORS: "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&q=80",
  SPECIALTY: "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=600&q=80",
};

const GLOBAL_FALLBACK = FALLBACKS.FINISHES;

export default function StyleImage({ src, category, alt, className, ...rest }) {
  const primary = src || FALLBACKS[category] || GLOBAL_FALLBACK;
  const handleError = (e) => {
    const el = e.currentTarget;
    const fallback = FALLBACKS[category] || GLOBAL_FALLBACK;
    if (el.src !== fallback) {
      el.src = fallback;
    } else if (el.dataset.fallbackLevel !== "final") {
      el.dataset.fallbackLevel = "final";
      el.src = GLOBAL_FALLBACK;
    }
  };
  return (
    <img
      src={primary}
      alt={alt || ""}
      className={className}
      loading="lazy"
      onError={handleError}
      {...rest}
    />
  );
}
