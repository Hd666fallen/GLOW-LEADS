"""Master library of 60 nail styles organized by category."""

# Category keys map to the tabs shown on the customer funnel
CATEGORIES = [
    "FINISHES",
    "FRENCH",
    "OMBRE",
    "NAIL_ART",
    "EMBELLISHMENTS",
    "COLORS",
    "SPECIALTY",
]

# Reusable image placeholders — all from Unsplash, curated nail art.
# Deterministic mapping keeps images consistent across refreshes.
_IMG = {
    "rose": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=600&q=80",
    "matte": "https://images.unsplash.com/photo-1610992015762-45dca7a1f6b9?w=600&q=80",
    "chrome": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=600&q=80",
    "glaze": "https://images.unsplash.com/photo-1604654894611-6973b56f6cc6?w=600&q=80",
    "french": "https://images.unsplash.com/photo-1519419691348-3b3433c4c20e?w=600&q=80",
    "ombre": "https://images.unsplash.com/photo-1607779097040-26e80aa78e66?w=600&q=80",
    "art": "https://images.unsplash.com/photo-1604654894710-3c7d74bfdb1e?w=600&q=80",
    "gems": "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=600&q=80",
    "red": "https://images.unsplash.com/photo-1601612628452-9e99ced43524?w=600&q=80",
    "nude": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&q=80",
    "pink": "https://images.unsplash.com/photo-1599948128020-9a44505b58bc?w=600&q=80",
    "black": "https://images.unsplash.com/photo-1607779097040-26e80aa78e66?w=600&q=80",
    "acrylic": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=600&q=80",
}


def _s(sid, name, category, description, price_low, price_high, image_key, prompt_hint):
    return {
        "id": sid,
        "name": name,
        "category": category,
        "description": description,
        "price_range": {"low": price_low, "high": price_high},
        "image": _IMG[image_key],
        "prompt_hint": prompt_hint,
    }


STYLES = [
    # FINISHES (1-11)
    _s("classic-gel", "Classic Gel", "FINISHES", "Glossy solid color, long lasting", 45, 65, "rose", "glossy classic gel manicure in soft rose pink"),
    _s("matte-gel", "Matte Gel", "FINISHES", "Velvety flat modern finish", 50, 70, "matte", "matte gel finish in muted mauve, velvety flat sheen"),
    _s("chrome", "Chrome", "FINISHES", "Mirror-like metallic high shine", 60, 85, "chrome", "mirror chrome metallic silver nails, ultra reflective"),
    _s("glazed-donut", "Glazed Donut", "FINISHES", "Sheer pearlescent glow", 55, 80, "glaze", "glazed donut pearlescent sheer nails, hailey bieber style"),
    _s("cat-eye", "Cat Eye", "FINISHES", "Magnetic 3D depth, moves in light", 60, 85, "chrome", "cat eye magnetic nails with shimmering 3d stripe in deep blue"),
    _s("jelly-glass", "Jelly Glass", "FINISHES", "Sheer translucent glossy", 50, 75, "glaze", "jelly glass translucent pink nails, glossy sheer"),
    _s("velvet-suede", "Velvet Suede", "FINISHES", "Textured soft matte", 55, 80, "matte", "velvet suede textured matte burgundy nails"),
    _s("holographic", "Holographic", "FINISHES", "Rainbow shifting glitter", 65, 90, "chrome", "holographic rainbow glitter nails, prismatic shine"),
    _s("iridescent", "Iridescent Duochrome", "FINISHES", "Color shifting by angle", 65, 90, "chrome", "iridescent duochrome nails shifting pink to purple"),
    _s("mirror-powder", "Mirror Powder", "FINISHES", "Ultra reflective finish", 65, 90, "chrome", "mirror powder chrome nails, flawless metallic"),
    _s("soap-nails", "Soap Nails", "FINISHES", "Ultra glossy clean look", 45, 65, "glaze", "soap nails ultra glossy clean sheer natural look"),
    # FRENCH (12-18)
    _s("french-classic", "Classic French Tip", "FRENCH", "White tips, natural base", 50, 70, "french", "classic french manicure, crisp white tips on natural pink base"),
    _s("french-colored", "Colored French Tip", "FRENCH", "Colored tips any color", 55, 75, "french", "colored french tip nails with pastel lilac tips"),
    _s("french-reverse", "Reverse French", "FRENCH", "Color at base not tip", 55, 75, "french", "reverse french manicure, black color at the cuticle base"),
    _s("french-ombre", "Ombre French", "FRENCH", "Gradient fade into tip", 60, 80, "ombre", "ombre french nails with soft pink to white fade"),
    _s("french-chrome", "Chrome French", "FRENCH", "Metallic tips", 60, 85, "chrome", "chrome french nails with silver mirror tips"),
    _s("french-micro", "Micro French", "FRENCH", "Ultra thin delicate tip", 55, 75, "french", "micro french nails with ultra thin delicate white tip"),
    _s("french-bold", "Bold French", "FRENCH", "Dramatic thick tip", 55, 75, "french", "bold thick french tip manicure, high contrast"),
    # OMBRE (19-23)
    _s("ombre-classic", "Classic Ombre", "OMBRE", "Two color fade", 55, 75, "ombre", "classic ombre nails fading pink to white"),
    _s("ombre-sunset", "Sunset Ombre", "OMBRE", "Orange/pink/purple tropical fade", 60, 85, "ombre", "sunset ombre nails with orange pink purple tropical gradient"),
    _s("aura-nails", "Aura Nails", "OMBRE", "Dreamy halo glow effect", 65, 90, "ombre", "aura nails with dreamy halo glow effect in pastel pink and purple"),
    _s("watercolor", "Watercolor", "OMBRE", "Soft blended pastel wash", 60, 85, "ombre", "watercolor nails with soft blended pastel wash"),
    _s("marble", "Marble", "OMBRE", "Stone swirl pattern", 60, 85, "art", "marble nails with elegant white and gold swirl pattern"),
    # NAIL ART (24-35)
    _s("floral-art", "Floral Art", "NAIL_ART", "Hand painted flowers", 70, 95, "art", "hand painted floral nail art with tiny daisies and roses"),
    _s("abstract-art", "Abstract Art", "NAIL_ART", "Free form color pops", 65, 90, "art", "abstract art nails with free form color pops and shapes"),
    _s("geometric", "Geometric", "NAIL_ART", "Lines, triangles, negative space", 65, 90, "art", "geometric nail art with clean lines triangles and negative space"),
    _s("animal-print", "Animal Print", "NAIL_ART", "Leopard or cheetah pattern", 65, 90, "art", "leopard print nail art in classic brown black tan"),
    _s("swirl-art", "Swirl Art", "NAIL_ART", "Y2K colorful swirls", 65, 90, "art", "y2k swirl nails with colorful pink blue green swirls"),
    _s("dots", "Minimalist Dots", "NAIL_ART", "Simple dot accents", 55, 75, "art", "minimalist nail art with delicate white dot accents on nude base"),
    _s("line-art", "Line Art", "NAIL_ART", "Thin elegant lines", 60, 80, "art", "line art nails with thin elegant black lines on nude"),
    _s("butterfly", "Butterfly Art", "NAIL_ART", "Delicate butterfly motifs", 70, 95, "art", "butterfly nail art with delicate painted butterflies"),
    _s("celestial", "Celestial Stars", "NAIL_ART", "Moons, stars, galaxy", 70, 95, "art", "celestial nail art with moons stars galaxy in deep blue and gold"),
    _s("fruit-art", "Fruit Art", "NAIL_ART", "Cherry, strawberry, lemon", 70, 95, "art", "cute fruit nail art with cherries and strawberries"),
    _s("holiday", "Holiday Seasonal", "NAIL_ART", "Christmas, Halloween, Valentine", 65, 90, "art", "festive holiday nail art with winter snowflakes and red accents"),
    _s("plaid", "Plaid Tartan", "NAIL_ART", "Checkered pattern", 65, 90, "art", "plaid tartan nail art in classic red green and white"),
    # EMBELLISHMENTS (36-42)
    _s("rhinestone", "Rhinestone Crystal", "EMBELLISHMENTS", "Swarovski gem accents", 75, 110, "gems", "rhinestone crystal nails with swarovski gem accents sparkling"),
    _s("pearl-accents", "Pearl Accents", "EMBELLISHMENTS", "Tiny pearl embellishments", 70, 100, "gems", "pearl accent nails with tiny white pearls on nude base"),
    _s("gold-foil", "Gold Foil", "EMBELLISHMENTS", "Real gold leaf details", 75, 110, "gems", "gold foil nails with real gold leaf details on nude base"),
    _s("3d-art", "3D Nail Art", "EMBELLISHMENTS", "Raised dimensional designs", 85, 120, "gems", "3d raised nail art with dimensional flower sculptures"),
    _s("charms", "Nail Charms", "EMBELLISHMENTS", "Metal charm attachments", 80, 115, "gems", "nail charms with dangling metal gold accessories"),
    _s("caviar", "Caviar Beads", "EMBELLISHMENTS", "Tiny bead texture", 70, 100, "gems", "caviar bead nails with tiny textured beads all over"),
    _s("glitter-ombre", "Glitter Ombre", "EMBELLISHMENTS", "Chunky or fine glitter fade", 65, 90, "ombre", "glitter ombre nails with fine silver glitter fading to tip"),
    # COLORS (43-55)
    _s("nude-milky", "Nude Milky", "COLORS", "Sheer natural skin tone", 45, 65, "nude", "milky sheer nude nails, classic natural clean look"),
    _s("classic-red", "Classic Red", "COLORS", "Bold timeless red", 45, 65, "red", "classic bold timeless red nails, glossy finish"),
    _s("deep-plum", "Deep Plum Berry", "COLORS", "Rich purple-red", 45, 65, "red", "deep plum berry nails in rich purple red"),
    _s("chocolate", "Chocolate Latte", "COLORS", "Warm earthy brown", 45, 65, "matte", "chocolate latte brown nails, warm earthy tone"),
    _s("baby-pink", "Baby Pink", "COLORS", "Soft feminine pink", 45, 65, "pink", "soft baby pink nails, feminine delicate"),
    _s("hot-pink", "Hot Pink Barbie", "COLORS", "Bold bright pink", 45, 65, "pink", "hot pink barbie nails, bold bright vivid"),
    _s("lavender", "Lavender Lilac", "COLORS", "Soft purple pastel", 45, 65, "pink", "lavender lilac soft purple pastel nails"),
    _s("sage-olive", "Sage Olive", "COLORS", "Earthy muted green", 45, 65, "matte", "sage olive earthy muted green nails"),
    _s("navy-blue", "Deep Navy Blue", "COLORS", "Rich ocean blue", 45, 65, "matte", "deep navy blue rich ocean nails"),
    _s("black", "Black", "COLORS", "Classic bold black", 45, 65, "black", "classic bold glossy black nails"),
    _s("white-cream", "White Cream", "COLORS", "Clean minimal white", 45, 65, "nude", "clean minimal white cream nails, fresh look"),
    _s("coral", "Coral Peach", "COLORS", "Warm orange-pink", 45, 65, "pink", "coral peach warm orange pink nails"),
    _s("butter-yellow", "Butter Yellow", "COLORS", "Soft warm yellow", 45, 65, "pink", "butter yellow soft warm pastel nails"),
    # SPECIALTY (56-60)
    _s("acrylic-full", "Acrylic Full Set", "SPECIALTY", "Sculpted acrylic extensions", 75, 110, "acrylic", "acrylic full set long almond nails in glossy pink"),
    _s("dip-powder", "Dip Powder", "SPECIALTY", "Long lasting dip color", 60, 85, "rose", "dip powder manicure in dusty rose, ultra durable finish"),
    _s("polygel", "Polygel", "SPECIALTY", "Hybrid gel-acrylic sculpted set", 75, 110, "acrylic", "polygel sculpted long nails, hybrid strength glossy"),
    _s("extensions", "Nail Extensions", "SPECIALTY", "Length added with forms or tips", 70, 100, "acrylic", "nail extensions in medium length coffin shape, glossy nude"),
    _s("repair", "Nail Repair", "SPECIALTY", "Fix broken natural nails", 25, 45, "nude", "natural nail repair, healthy strengthened clean finish"),
]

assert len(STYLES) == 60, f"Expected 60 styles, got {len(STYLES)}"

STYLE_MAP = {s["id"]: s for s in STYLES}
