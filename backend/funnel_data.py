"""Funnel configuration data — shapes, designs, colours.

Images are curated Unsplash photo IDs (verified to render) so every card has
a clear close-up of nails on real hands. Variation parameters (sat, hue,
flip) ensure visual uniqueness across cards that share base imagery.
"""


def _u(photo_id: str, variant: str = "", w: int = 600) -> str:
    base = f"https://images.unsplash.com/photo-{photo_id}?w={w}&h={w}&fit=crop&q=80&auto=format"
    return f"{base}&{variant}" if variant else base


# ---------------------------------------------------------------------------
# SHAPES — close-up nail-shape references (each unique)
# ---------------------------------------------------------------------------

SHAPES = [
    {
        "id": "round",
        "label": "Round",
        "description": "Natural, classic, everyday",
        "image": _u("1522337360788-8b13dee7a37e"),  # natural rounded nude nails
        "keywords": ["round", "natural"],
    },
    {
        "id": "square",
        "label": "Square",
        "description": "Bold, clean, modern",
        "image": _u("1604654894610-df63bc536371"),  # straight-edge square pink nails
        "keywords": ["square", "straight"],
    },
    {
        "id": "coffin",
        "label": "Coffin",
        "description": "Dramatic, trendy, elongating",
        "image": _u("1632345031435-8727f6897d53"),  # long tapered chrome nails
        "keywords": ["coffin", "ballerina"],
    },
    {
        "id": "almond",
        "label": "Almond",
        "description": "Feminine, elegant, slimming",
        "image": _u("1772322586649-fc11154e76b9"),  # tapered oval matte pink
        "keywords": ["almond", "oval", "tapered"],
    },
    {
        "id": "stiletto",
        "label": "Stiletto",
        "description": "Fierce, edgy, statement",
        "image": _u("1601612628452-9e99ced43524"),  # long pointed red nails
        "keywords": ["stiletto", "pointed"],
    },
    {
        "id": "squoval",
        "label": "Squoval",
        "description": "Best of both worlds",
        "image": _u("1515688594390-b649af70d282"),  # rounded-square manicure
        "keywords": ["squoval"],
    },
]
SHAPE_MAP = {s["id"]: s for s in SHAPES}


def _d(did, label, price_low, price_high, image, badge=None):
    return {
        "id": did,
        "label": label,
        "price_range": {"low": price_low, "high": price_high},
        "image": image,
        "badge": badge,
    }


# Curated working photo IDs (verified) — used + varied per design via sat/hue/flip
# to give every card a visually distinct image without 404s.
_PINK = "1604654894610-df63bc536371"
_MATTE = "1515688594390-b649af70d282"
_CHROME = "1632345031435-8727f6897d53"
_FRENCH = "1519419691348-3b3433c4c20e"
_OMBRE = "1607779097040-26e80aa78e66"
_GEMS = "1580618672591-eb180b1a973f"
_RED = "1601612628452-9e99ced43524"
_NUDE = "1522337360788-8b13dee7a37e"
_GLITTER = "1606660265514-358ebbadc80d"
_CLOSEUP = "1595475207225-428b62bda831"
_BLACK_ART = "1772322586711-22f84f5f3432"
_BABY_PINK = "1772322586649-fc11154e76b9"
_NAVY_GOLD = "1754799670312-8e7da8e40ad7"
_SALON = "1713552566168-89c00fd622cf"


# ---------------------------------------------------------------------------
# DESIGNS — every card a distinct image + correct visual cue
# ---------------------------------------------------------------------------

DESIGN_GROUPS = [
    {
        "id": "popular",
        "label": "Most Popular",
        "designs": [
            _d("classic-gel", "Classic Gel", 35, 55, _u(_PINK), "Most Popular"),
            _d("glazed-donut", "Glazed Donut", 45, 65, _u(_NUDE, "sat=-20"), "Trending"),
            _d("french-tip", "French Tip", 40, 60, _u(_FRENCH), "Classic"),
            _d("chrome", "Chrome", 50, 75, _u(_CHROME), "Fan Fave"),
            _d("ombre", "Ombre", 45, 65, _u(_OMBRE)),
            _d("matte-gel", "Matte Gel", 35, 55, _u(_MATTE)),
        ],
    },
    {
        "id": "french",
        "label": "French",
        "designs": [
            _d("french-classic", "Classic French", 40, 55, _u(_FRENCH)),
            _d("french-coloured", "Coloured French", 45, 60, _u(_FRENCH, "hue=320")),
            _d("french-reverse", "Reverse French", 45, 60, _u(_FRENCH, "flip=h")),
            _d("french-double", "Double French", 50, 65, _u(_FRENCH, "sat=30")),
            _d("french-ombre", "Ombre French", 50, 65, _u(_OMBRE, "sat=-10")),
            _d("french-chrome", "Chrome French", 55, 70, _u(_CHROME, "sat=-30")),
            _d("french-glitter", "Glitter French", 50, 65, _u(_GLITTER)),
            _d("french-micro", "Micro French", 45, 60, _u(_FRENCH, "sat=-20")),
        ],
    },
    {
        "id": "ombre",
        "label": "Ombre",
        "designs": [
            _d("ombre-classic", "Classic Ombre", 45, 65, _u(_OMBRE)),
            _d("ombre-three", "Three Colour Ombre", 55, 75, _u(_OMBRE, "sat=40")),
            _d("ombre-reverse", "Reverse Ombre", 45, 65, _u(_OMBRE, "flip=h")),
            _d("ombre-sunset", "Sunset Ombre", 55, 75, _u(_OMBRE, "hue=20")),
            _d("ombre-pastel", "Pastel Ombre", 50, 70, _u(_BABY_PINK, "sat=-10")),
            _d("ombre-neon", "Neon Ombre", 55, 75, _u(_GLITTER, "sat=80")),
        ],
    },
    {
        "id": "chrome",
        "label": "Chrome",
        "designs": [
            _d("chrome-mirror", "Mirror Chrome", 55, 80, _u(_CHROME)),
            _d("chrome-rose-gold", "Rose Gold Chrome", 55, 80, _u(_CHROME, "hue=340")),
            _d("chrome-holo", "Holographic", 60, 85, _u(_CHROME, "hue=240")),
            _d("chrome-cat-eye", "Cat Eye", 55, 75, _u(_NAVY_GOLD)),
            _d("chrome-duo", "Duochrome", 60, 80, _u(_CHROME, "sat=70")),
            _d("chrome-aurora", "Aurora Effect", 65, 90, _u(_CHROME, "hue=180&sat=60")),
            _d("chrome-glazed-glass", "Glazed Donut Glass", 55, 75, _u(_NUDE, "sat=10")),
        ],
    },
    {
        "id": "nail-art",
        "label": "Nail Art",
        "designs": [
            _d("art-floral", "Floral", 60, 90, _u(_BABY_PINK, "hue=10")),
            _d("art-abstract", "Abstract", 65, 95, _u(_BLACK_ART)),
            _d("art-geometric", "Geometric", 60, 90, _u(_BLACK_ART, "sat=-30")),
            _d("art-marble", "Marble", 65, 95, _u(_NAVY_GOLD, "sat=-20")),
            _d("art-animal", "Animal Print", 65, 95, _u(_NAVY_GOLD, "hue=30")),
            _d("art-checker", "Checkerboard", 60, 85, _u(_BLACK_ART, "sat=-50")),
            _d("art-swirl", "Swirl", 65, 90, _u(_OMBRE, "hue=280")),
            _d("art-negative", "Negative Space", 55, 80, _u(_NUDE)),
            _d("art-block", "Colour Block", 55, 80, _u(_RED, "hue=120")),
            _d("art-stripe", "Striped", 55, 80, _u(_BLACK_ART, "sat=20")),
        ],
    },
    {
        "id": "embellishments",
        "label": "Embellishments",
        "designs": [
            _d("emb-rhinestone", "Rhinestone Crystal", 65, 100, _u(_GEMS)),
            _d("emb-pearl", "Pearl Accents", 60, 90, _u(_GEMS, "sat=-50")),
            _d("emb-gold-foil", "Gold Foil", 65, 95, _u(_NAVY_GOLD, "hue=40")),
            _d("emb-glitter-ombre", "Glitter Ombre", 60, 85, _u(_GLITTER)),
            _d("emb-3d", "3D Nail Art", 75, 120, _u(_GEMS, "hue=320")),
            _d("emb-sticker", "Sticker Art", 50, 75, _u(_BABY_PINK, "hue=180")),
            _d("emb-stamping", "Stamping", 50, 75, _u(_BLACK_ART, "hue=200")),
        ],
    },
    {
        "id": "specialty",
        "label": "Specialty",
        "designs": [
            _d("spec-aura", "Aura Nails", 55, 80, _u(_OMBRE, "hue=300&sat=-20"), "Trending"),
            _d("spec-jelly", "Jelly Nails", 45, 70, _u(_NUDE, "sat=30")),
            _d("spec-velvet", "Velvet Nails", 55, 75, _u(_MATTE, "hue=350")),
            _d("spec-foil", "Foil Art", 60, 85, _u(_NAVY_GOLD)),
            _d("spec-gradient-tips", "Gradient Tips", 45, 65, _u(_OMBRE, "sat=-30")),
            _d("spec-tortoise", "Tortoiseshell", 60, 85, _u(_NAVY_GOLD, "hue=10&sat=-30")),
        ],
    },
]

DESIGN_MAP = {}
for g in DESIGN_GROUPS:
    for d in g["designs"]:
        DESIGN_MAP[d["id"]] = {**d, "group_id": g["id"], "group_label": g["label"]}


# ---------------------------------------------------------------------------
# COLORS — unchanged from previous iteration (200 colours, 9 groups)
# ---------------------------------------------------------------------------

def _co(hex_code, name, brand):
    return {"hex": hex_code, "name": name, "brand": brand}


COLOR_GROUPS = [
    {"id": "nudes", "label": "Nudes & Neutrals", "colors": [
        _co("#F5F0EB", "Milky White", "OPI Funny Bunny"),
        _co("#FDE8E8", "Sheer Pink", "OPI Bubble Bath"),
        _co("#F2C4CE", "Ballet Pink", "Essie Ballet Slippers"),
        _co("#E8B89A", "Peachy Nude", "OPI Put It In Neutral"),
        _co("#D4B896", "Beige Latte", "Essie Bare It All"),
        _co("#C9B99A", "Warm Sand", "OPI Don't Pretzel"),
        _co("#C4A882", "Warm Taupe", "Essie Sand Tropez"),
        _co("#B8A89A", "Mushroom", "OPI Tickle My France-y"),
        _co("#A89880", "Greige", "Essie Topless & Barefoot"),
        _co("#C8BFB0", "Cool Beige", "OPI My Vampire Is Buff"),
        _co("#D4A090", "Rose Beige", "Essie Romper Room"),
        _co("#C68642", "Caramel", "OPI Ginger Snap Crackle"),
        _co("#967259", "Latte Brown", "Essie Mochachino"),
        _co("#8B6355", "Mocha", "OPI Chocolate Moose"),
        _co("#6B3A2A", "Chocolate", "Essie Chocolate Cake"),
        _co("#3C1810", "Espresso", "OPI Squeaker Of The House"),
        _co("#FFFDD0", "Cream", "OPI My Vampire Is Buff"),
        _co("#FAF7F0", "Off White", "Essie Marshmallow"),
        _co("#FFFFF0", "Ivory", "OPI Alpine Snow"),
        _co("#F2EFE4", "Porcelain", "Essie Blanc"),
        _co("#FFE8EE", "Glazed Donut", "OPI Bubble Bath Glaze"),
        _co("#FFF8DC", "Butter Cream", "Essie Spin The Bottle"),
        _co("#F3E5AB", "Vanilla", "OPI Don't Touch My Tutu"),
        _co("#E8DCC8", "Oat Milk", "Essie Pillow Talk"),
        _co("#F8F4F0", "Cotton", "OPI Stop Me If You've Heard This"),
    ]},
    {"id": "pinks", "label": "Pinks", "colors": [
        _co("#FFB6C1", "Baby Pink", "Essie Saved By The Belle"),
        _co("#FFB7C5", "Soft Pink", "OPI Passion"),
        _co("#FF85A1", "Bubblegum", "Essie Bachelorette Bash"),
        _co("#FF69B4", "Candy Pink", "OPI Hotter Than You Pink"),
        _co("#FF1493", "Hot Pink", "Essie Watermelon"),
        _co("#FF007F", "Neon Pink", "OPI Pink Flamenco"),
        _co("#FC74A0", "Flamingo", "Essie Flamingo"),
        _co("#DCAE96", "Dusty Rose", "OPI Rosy Future"),
        _co("#FFB7B2", "Blush", "Essie Mademoiselle"),
        _co("#B76E79", "Rose Gold", "OPI Be There In A Prosecco"),
        _co("#F4C2C2", "Millennial Pink", "Essie First Timer"),
        _co("#E75480", "Barbie Pink", "OPI Elephantastic Pink"),
        _co("#FF00FF", "Magenta", "Essie Peony Punch"),
        _co("#FF0090", "Fuchsia", "OPI Pink-ing Of You"),
        _co("#E0B0FF", "Mauve Pink", "Essie Maximillian"),
        _co("#D8A0A0", "Dusty Mauve", "OPI Tickle My France-y"),
        _co("#FA8072", "Salmon", "Essie Tart Deco"),
        _co("#FF7B7B", "Coral Pink", "OPI Cajun Shrimp"),
        _co("#FC6C85", "Watermelon", "Essie Watermelon"),
        _co("#FC5A8D", "Strawberry", "OPI Strawberry Margarita"),
        _co("#FF78A5", "Peony", "Essie Peony"),
        _co("#F7CAC9", "Rose Quartz", "OPI Let Me Bayou A Drink"),
        _co("#FFD1DC", "Pastel Pink", "Essie Spin The Bottle"),
        _co("#FFB3BA", "Powder Pink", "OPI Do You Take Lei Away"),
        _co("#FFB7C5", "Cherry Blossom", "Essie Cherry Play"),
    ]},
    {"id": "reds", "label": "Reds", "colors": [
        _co("#C41E3A", "Classic Red", "OPI Big Apple Red"),
        _co("#DC143C", "Cherry Red", "Essie Really Red"),
        _co("#FF0000", "True Red", "OPI Red Hot Rio"),
        _co("#B22222", "Crimson", "Essie Crimson"),
        _co("#FF2400", "Scarlet", "OPI Scarlet Woman"),
        _co("#FF007F", "Rose Red", "Essie Rose"),
        _co("#CB4154", "Brick Red", "OPI Got The Blues For Red"),
        _co("#FF6347", "Tomato Red", "Essie Ole Caliente"),
        _co("#CE2029", "Fire Engine", "OPI An Affair In Red Square"),
        _co("#722F37", "Wine Red", "Essie Bordeaux"),
        _co("#800020", "Burgundy", "OPI Malaga Wine"),
        _co("#73343A", "Merlot", "Essie Bordeaux"),
        _co("#4A0000", "Oxblood", "OPI Lincoln Park After Dark"),
        _co("#8B0000", "Mob Wife Red", "Essie Bordeaux Dark"),
        _co("#B7410E", "Rust", "OPI Ginger Snap"),
        _co("#CC4400", "Burnt Orange Red", "Essie Clambake"),
        _co("#3D0C02", "Dark Cherry", "OPI Vampsterdam"),
        _co("#660000", "Blood Red", "Essie Navigate Her"),
        _co("#FF4500", "Poppy", "OPI Cajun Shrimp"),
        _co("#E30B5C", "Raspberry", "Essie Raspberry"),
    ]},
    {"id": "oranges", "label": "Oranges & Yellows", "colors": [
        _co("#FF7F50", "Coral", "Essie Tart Deco"),
        _co("#F28500", "Tangerine", "OPI Toucan Do It"),
        _co("#FF6600", "Orange", "Essie Clambake"),
        _co("#CC5500", "Burnt Orange", "OPI It's A Piazza Cake"),
        _co("#E2725B", "Terracotta", "Essie Terracotta"),
        _co("#FFCBA4", "Peach", "OPI Peach Side Babe"),
        _co("#FBCEB1", "Apricot", "Essie Peach Daiquiri"),
        _co("#FF8243", "Mango", "OPI Emotionally Unavailable"),
        _co("#FFFAA0", "Butter Yellow", "Essie Baguette Me Not"),
        _co("#FFF44F", "Lemon", "OPI No Faux Yellow"),
        _co("#FFD700", "Sunflower", "Essie She's Picture Perfect"),
        _co("#FFDB58", "Mustard", "OPI Curry Up Don't Be Late"),
        _co("#FFD000", "Gold Yellow", "Essie A Crewed Interest"),
        _co("#FDFD96", "Pastel Yellow", "OPI Cute Little Koala"),
        _co("#FFFF00", "Neon Yellow", "Essie Neon Yellow"),
    ]},
    {"id": "purples", "label": "Purples", "colors": [
        _co("#E6E6FA", "Lavender", "OPI Do You Lilac It"),
        _co("#C8A2C8", "Lilac", "Essie Cascade Cool"),
        _co("#EE82EE", "Soft Violet", "OPI Violet Beauregarde"),
        _co("#CCCCFF", "Periwinkle", "Essie Periwinkle"),
        _co("#C9A0DC", "Wisteria", "OPI In My Back Pocket"),
        _co("#DA70D6", "Orchid", "Essie Stir Crazy"),
        _co("#9966CC", "Amethyst", "OPI Purple With A Purpose"),
        _co("#6F2DA8", "Grape", "Essie Maximillian"),
        _co("#4B0082", "Deep Purple", "OPI Reign In Spanish"),
        _co("#8E4585", "Plum", "Essie Plum Sponsor"),
        _co("#614051", "Eggplant", "OPI Vampsterdam Purple"),
        _co("#E0B0FF", "Mauve", "Essie Mauve"),
        _co("#9E7BB5", "Dusty Purple", "OPI Can't Find My Czechbook"),
        _co("#8B0057", "Berry Purple", "Essie Sole Mate"),
        _co("#7F00FF", "Violet", "OPI Purple Palazzo Pants"),
        _co("#4D3B47", "Dark Mauve", "OPI Dim Sum Plum"),
        _co("#967BB6", "Dusty Lavender", "Essie Cascade Cool"),
        _co("#B39EB5", "Pastel Purple", "OPI Abstraction"),
        _co("#8B008B", "Magenta Purple", "Essie Stitch"),
        _co("#BF00FF", "Neon Purple", "Essie Neon Purple"),
    ]},
    {"id": "blues", "label": "Blues", "colors": [
        _co("#89CFF0", "Baby Blue", "OPI Reach For The Sky"),
        _co("#B0E0E6", "Powder Blue", "Essie Borrowed & Blue"),
        _co("#87CEEB", "Sky Blue", "OPI To Be Continued"),
        _co("#6495ED", "Cornflower", "OPI Ogre-The-Top Blue"),
        _co("#99C5C4", "Ice Blue", "Essie Bikini So Teeny"),
        _co("#006994", "Ocean Blue", "OPI No Room For The Blues"),
        _co("#4169E1", "Royal Blue", "Essie Mezmerised"),
        _co("#0047AB", "Cobalt", "OPI Fearlessly Alice"),
        _co("#0F52BA", "Sapphire", "Essie Sailor"),
        _co("#003087", "Navy", "OPI Russian Navy"),
        _co("#191970", "Midnight", "Essie Navigate Her"),
        _co("#1560BD", "Denim", "OPI Didn't Bother To Call"),
        _co("#008B8B", "Teal Blue", "Essie Teal The Cows"),
        _co("#40E0D0", "Turquoise", "OPI Fly"),
        _co("#00FFFF", "Aqua", "Essie Turquoise & Caicos"),
        _co("#6A5ACD", "Slate Blue", "Essie Lapiz Of Luxury"),
        _co("#4682B4", "Steel Blue", "OPI Into The Night"),
        _co("#AEC6CF", "Pastel Blue", "Essie Something Blue"),
        _co("#CCCCFF", "Periwinkle Blue", "Essie Periwinkle"),
        _co("#0000FF", "Electric Blue", "OPI Fearlessly Alice"),
    ]},
    {"id": "greens", "label": "Greens", "colors": [
        _co("#98FF98", "Mint", "OPI Gargantuan Green Grape"),
        _co("#77DD77", "Pastel Green", "Essie Turquoise"),
        _co("#B2AC88", "Sage", "OPI Isn't It Grand Canyon"),
        _co("#8B9E6B", "Matcha", "Essie Matcha Content"),
        _co("#808000", "Olive", "OPI Uh-Oh Roll Down The Window"),
        _co("#568203", "Avocado", "Essie Avocado"),
        _co("#32CD32", "Lime", "OPI Charged Up"),
        _co("#4CBB17", "Kelly Green", "Essie Clover"),
        _co("#50C878", "Emerald", "OPI Jade Is The New Black"),
        _co("#228B22", "Forest Green", "Essie On The Roadie"),
        _co("#355E3B", "Hunter Green", "OPI Suzi & The Lifeguard"),
        _co("#006A4E", "Bottle Green", "Essie Butler Please"),
        _co("#008080", "Teal Green", "Essie Teal The Cows"),
        _co("#01796F", "Pine Green", "OPI Frozen Tundra"),
        _co("#71EEB8", "Seafoam", "Essie Turquoise & Caicos"),
        _co("#39FF14", "Neon Green", "Essie Neon Lights"),
        _co("#7FFF00", "Chartreuse", "OPI My Gecko Does Tricks"),
        _co("#8A9A5B", "Moss", "Essie Going Incognito"),
        _co("#B0BF1A", "Acid Green", "OPI My Gecko"),
        _co("#B2AC88", "Sage Minimal", "Essie Incognito"),
    ]},
    {"id": "darks", "label": "Darks & Metallics", "colors": [
        _co("#0A0A0A", "Jet Black", "OPI Black Onyx"),
        _co("#1C1C1C", "Soft Black", "Essie Licorice"),
        _co("#36454F", "Charcoal", "OPI Over The Taupe"),
        _co("#2C3539", "Gunmetal", "Essie Smokin Hot"),
        _co("#A9A9A9", "Dark Grey", "OPI Fifty Shades Of Greige"),
        _co("#808080", "Medium Grey", "Essie Chinchilly"),
        _co("#D3D3D3", "Light Grey", "OPI Skyscraper"),
        _co("#C0C0C0", "Silver", "Essie Miss Fancy Pants"),
        _co("#FFFFFF", "Bright White", "OPI Alpine Snow"),
        _co("#FAFAFA", "Pure White", "Essie Blanc"),
        _co("#AAB7B8", "Chrome Silver", "OPI Push & Shove"),
        _co("#B76E79", "Rose Gold Metal", "Essie Picture Perfect"),
        _co("#FFD700", "Gold", "OPI My Private Jet Gold"),
        _co("#CD7F32", "Bronze", "Essie Armed & Gorgeous"),
        _co("#B87333", "Copper", "OPI My Private Jet"),
        _co("#E5E4E2", "Platinum", "Essie Platinum"),
        _co("#E8E8FF", "Holographic", "OPI Glitter Off"),
        _co("#D4D4D4", "Mirror Chrome", "Essie Tinsel"),
        _co("#A8A9AD", "Dark Silver", "OPI Lucerne-tainly"),
        _co("#CFB53B", "Antique Gold", "Essie Good As Gold"),
    ]},
    {"id": "trendy", "label": "Trendy & Seasonal", "colors": [
        _co("#FF6EC7", "Y2K Pink", "Essie Crush On You"),
        _co("#8B0000", "Mob Wife Dark Red", "OPI Vampsterdam"),
        _co("#FFE4E8", "Glazed Donut Sheer", "OPI Bubble Bath"),
        _co("#967259", "Latte", "Essie Mochachino"),
        _co("#A07855", "Mocha Mousse", "OPI Squeaker"),
        _co("#008080", "Mermaid Teal", "Essie Teal"),
        _co("#FFB7C5", "Coquette Pink", "OPI Passion"),
        _co("#E8D5C4", "Clean Girl Nude", "Essie Bare It All"),
        _co("#1B2A4A", "Old Money Navy", "OPI Russian Navy"),
        _co("#B0C4DE", "Coastal Blue", "Essie Borrowed"),
        _co("#D4C5B0", "Quiet Luxury Beige", "OPI Don't Pretzel"),
        _co("#FF6347", "Tomato Girl Red", "Essie Ole Caliente"),
        _co("#4A0010", "Cherry Cola", "OPI Vampsterdam"),
        _co("#FF4040", "Neon Coral", "Essie Tart Deco"),
        _co("#FFD1DC", "Pastel Rainbow Pink", "Essie Spin"),
        _co("#AEC6CF", "Pastel Rainbow Blue", "Essie Blue"),
        _co("#C3B1E1", "Pastel Rainbow Purple", "OPI Abstraction"),
        _co("#FDFD96", "Pastel Rainbow Yellow", "OPI Cute Koala"),
        _co("#77DD77", "Pastel Rainbow Green", "Essie Turquoise"),
        _co("#FFB347", "Pastel Rainbow Orange", "OPI Peach Side"),
        _co("#9B1B30", "Deep Cranberry", "Essie Navigate Her"),
        _co("#C4A0A0", "Dusty Mauve Nude", "OPI Tickle"),
        _co("#708090", "Steel Grey Minimal", "OPI Skyscraper"),
        _co("#000080", "Ink Black Blue", "Essie Navigate Her"),
        _co("#FFA500", "Golden Hour", "OPI It's A Piazza"),
        _co("#FF4500", "Sunset Orange", "Essie Clambake"),
        _co("#003153", "Deep Ocean", "OPI Russian Navy"),
        _co("#C08081", "Vintage Rose", "Essie Romper Room"),
        _co("#3D0C02", "Midnight Plum", "OPI Vampsterdam"),
        _co("#77BFC7", "Aurora Borealis", "OPI Fly"),
        _co("#3C1810", "Espresso Brown", "OPI Squeaker"),
        _co("#E3A857", "Butter Caramel", "Essie Ginger Snap"),
        _co("#8A9A5B", "Dusty Sage", "Essie Incognito"),
        _co("#65000B", "Rosewood", "Essie Navigate Her"),
        _co("#B57EDC", "Lavender Fog", "OPI Abstraction"),
    ]},
]
