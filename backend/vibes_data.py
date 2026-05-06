"""Vibes, curated color palettes, extended 150-color palette, and style groupings
for the new 3-layer customer funnel (Vibe → Colour → Style).
"""

# ---------------------------------------------------------------------------
# VIBES — 5 mood archetypes with 8 hero colours each
# ---------------------------------------------------------------------------

def _c(hex_code, name, brand):
    return {"hex": hex_code, "name": name, "brand": brand}


VIBES = [
    {
        "id": "clean-minimal",
        "emoji": "🤍",
        "label": "Clean & Minimal",
        "tagline": "Quiet luxury, understated elegance",
        "hero_image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&q=80",
        "preview_colors": ["#F5F0EB", "#E8DCC8", "#F2C4CE", "#FFE8EE"],
        "colors": [
            _c("#F5F0EB", "Milky White", "OPI Funny Bunny"),
            _c("#E8DCC8", "Oat Milk", "Essie Pillow Talk"),
            _c("#F2C4CE", "Ballet Pink", "Essie Ballet Slippers"),
            _c("#FFE8EE", "Glazed Donut", "OPI Bubble Bath"),
            _c("#E8D5C4", "Clean Girl Nude", "Essie Bare It All"),
            _c("#D4C5B0", "Quiet Luxury Beige", "OPI Don't Pretzel"),
            _c("#F2EFE4", "Porcelain", "Essie Blanc"),
            _c("#967259", "Latte Brown", "Essie Mochachino"),
        ],
    },
    {
        "id": "soft-feminine",
        "emoji": "🌸",
        "label": "Soft & Feminine",
        "tagline": "Pretty, romantic, girly",
        "hero_image": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&q=80",
        "preview_colors": ["#FFB6C1", "#FFB7B2", "#F7CAC9", "#E6E6FA"],
        "colors": [
            _c("#FFB6C1", "Baby Pink", "Essie Saved By The Belle"),
            _c("#FFB7B2", "Blush", "Essie Mademoiselle"),
            _c("#F7CAC9", "Rose Quartz", "OPI Let Me Bayou A Drink"),
            _c("#DCAE96", "Dusty Rose", "OPI Rosy Future"),
            _c("#FFB7C5", "Cherry Blossom", "Essie Cherry Play"),
            _c("#E6E6FA", "Lavender", "OPI Do You Lilac It"),
            _c("#F8B4C8", "Coquette Pink", "OPI Passion"),
            _c("#FF78A5", "Peony", "Essie Peony"),
        ],
    },
    {
        "id": "bold-edgy",
        "emoji": "🖤",
        "label": "Bold & Edgy",
        "tagline": "Dark, dramatic, statement",
        "hero_image": "https://images.unsplash.com/photo-1772322586711-22f84f5f3432?w=800&q=80",
        "preview_colors": ["#0A0A0A", "#8B0000", "#4B0082", "#191970"],
        "colors": [
            _c("#0A0A0A", "Jet Black", "OPI Black Onyx"),
            _c("#8B0000", "Mob Wife Red", "OPI Vampsterdam"),
            _c("#4B0082", "Deep Purple", "OPI Reign In Spanish"),
            _c("#4A0000", "Oxblood", "OPI Lincoln Park After Dark"),
            _c("#191970", "Midnight", "Essie Navigate Her"),
            _c("#3D0C02", "Dark Cherry", "OPI Vampsterdam"),
            _c("#2C3539", "Gunmetal", "Essie Smokin Hot"),
            _c("#614051", "Eggplant", "OPI Vampsterdam Purple"),
        ],
    },
    {
        "id": "fun-trendy",
        "emoji": "✨",
        "label": "Fun & Trendy",
        "tagline": "Colourful, playful, Y2K vibes",
        "hero_image": "https://images.unsplash.com/photo-1599948128020-9a44505b58bc?w=800&q=80",
        "preview_colors": ["#FF6EC7", "#FF4040", "#0000FF", "#39FF14"],
        "colors": [
            _c("#FF6EC7", "Y2K Pink", "Essie Crush On You"),
            _c("#FF4040", "Neon Coral", "Essie Tart Deco"),
            _c("#0000FF", "Electric Blue", "OPI Fearlessly Alice"),
            _c("#E8E8FF", "Holographic", "OPI Glitter Off"),
            _c("#FFFAA0", "Butter Yellow", "Essie Baguette Me Not"),
            _c("#008080", "Mermaid Teal", "Essie Teal"),
            _c("#39FF14", "Neon Green", "Essie Neon Lights"),
            _c("#77BFC7", "Aurora Borealis", "OPI Fly"),
        ],
    },
    {
        "id": "classic-timeless",
        "emoji": "💅",
        "label": "Classic & Timeless",
        "tagline": "Polished, professional, clean",
        "hero_image": "https://images.unsplash.com/photo-1601612628452-9e99ced43524?w=800&q=80",
        "preview_colors": ["#C41E3A", "#F2C4CE", "#003087", "#800020"],
        "colors": [
            _c("#C41E3A", "Classic Red", "OPI Big Apple Red"),
            _c("#F2C4CE", "Ballet Pink", "Essie Ballet Slippers"),
            _c("#003087", "Navy", "OPI Russian Navy"),
            _c("#800020", "Burgundy", "OPI Malaga Wine"),
            _c("#FFFFFF", "Bright White", "OPI Alpine Snow"),
            _c("#B76E79", "Rose Gold", "OPI Be There In A Prosecco"),
            _c("#D4B896", "Nude Beige", "Essie Bare It All"),
            _c("#DC143C", "Cherry Red", "Essie Really Red"),
        ],
    },
]

VIBE_MAP = {v["id"]: v for v in VIBES}


# ---------------------------------------------------------------------------
# EXTENDED PALETTE — ~150 colours grouped by family
# ---------------------------------------------------------------------------

EXTENDED_PALETTE = [
    {"group": "Nudes", "colors": [
        _c("#F5F0EB", "Milky White", "OPI"),
        _c("#F2EFE4", "Porcelain", "Essie Blanc"),
        _c("#E8DCC8", "Oat Milk", "Essie Pillow Talk"),
        _c("#E8D5C4", "Clean Girl Nude", "Essie Bare It All"),
        _c("#D4B896", "Nude Beige", "Essie Bare It All"),
        _c("#D4C5B0", "Quiet Luxury", "OPI Don't Pretzel"),
        _c("#C8B7A6", "Sand Dune", "Essie Sand Tropez"),
        _c("#BFA388", "Almond", "OPI Samoan Sand"),
        _c("#A68A6D", "Caramel Latte", "Essie Latte Da"),
        _c("#967259", "Latte Brown", "Essie Mochachino"),
        _c("#E8C5A0", "Peach Nude", "Essie Topless & Barefoot"),
        _c("#F0D5C0", "Champagne", "OPI Passion"),
        _c("#EBDBC6", "Linen", "Essie Body Language"),
        _c("#D9BFA6", "Taupe", "OPI Tiramisu for Two"),
        _c("#C9AA89", "Mushroom", "Essie Fierce No Fear"),
    ]},
    {"group": "Pinks", "colors": [
        _c("#FFB6C1", "Baby Pink", "Essie Saved By The Belle"),
        _c("#FFB7B2", "Blush", "Essie Mademoiselle"),
        _c("#F2C4CE", "Ballet Pink", "Essie Ballet Slippers"),
        _c("#FFE8EE", "Glazed Donut", "OPI Bubble Bath"),
        _c("#F7CAC9", "Rose Quartz", "OPI Let Me Bayou A Drink"),
        _c("#FFB7C5", "Cherry Blossom", "Essie Cherry Play"),
        _c("#FF78A5", "Peony", "Essie Peony"),
        _c("#FF6EC7", "Y2K Pink", "Essie Crush On You"),
        _c("#E94B8C", "Bright Pink", "Essie Bachelorette Bash"),
        _c("#DB7093", "Rose Pink", "OPI Aphrodite's Pink"),
        _c("#DCAE96", "Dusty Rose", "OPI Rosy Future"),
        _c("#D88FB1", "Mauve", "Essie Angora Cardi"),
        _c("#F8B4C8", "Coquette Pink", "OPI Passion"),
        _c("#E8A0BF", "Pink Punch", "Essie Punchy Pink"),
        _c("#FF1493", "Hot Pink Barbie", "OPI Kiss Me I'm Brazilian"),
    ]},
    {"group": "Reds", "colors": [
        _c("#C41E3A", "Classic Red", "OPI Big Apple Red"),
        _c("#DC143C", "Cherry Red", "Essie Really Red"),
        _c("#B22222", "Fire Engine", "OPI Red My Fortune Cookie"),
        _c("#800020", "Burgundy", "OPI Malaga Wine"),
        _c("#8B0000", "Mob Wife Red", "OPI Vampsterdam"),
        _c("#4A0000", "Oxblood", "OPI Lincoln Park After Dark"),
        _c("#B43E3E", "Brick Red", "Essie Berried Treasures"),
        _c("#CC3333", "Tomato", "OPI She's A Bad Muffuletta"),
        _c("#FF4040", "Neon Coral", "Essie Tart Deco"),
        _c("#E65050", "Poppy", "OPI Cajun Shrimp"),
        _c("#9B111E", "Ruby", "Essie Forever Yummy"),
        _c("#7D0A0A", "Wine", "OPI Malaga Wine"),
    ]},
    {"group": "Oranges", "colors": [
        _c("#FF8C42", "Tangerine", "Essie Saturday Disco Fever"),
        _c("#FF7043", "Sunset Orange", "OPI Suzi The First Lady"),
        _c("#FF6F20", "Pumpkin", "Essie Fall Harvest"),
        _c("#F57C00", "Marigold", "OPI Can't Find My Czechbook"),
        _c("#FFA07A", "Peachy", "Essie Peach Side Babe"),
        _c("#FF9966", "Coral", "OPI Cajun Shrimp"),
        _c("#E87A5D", "Terracotta", "OPI Freedom of Peach"),
        _c("#CC5500", "Burnt Orange", "Essie Clutch Me"),
    ]},
    {"group": "Purples", "colors": [
        _c("#4B0082", "Deep Purple", "OPI Reign In Spanish"),
        _c("#614051", "Eggplant", "OPI Vampsterdam"),
        _c("#8A2BE2", "Violet", "Essie Sexy Divide"),
        _c("#9370DB", "Medium Purple", "OPI Do You Lilac It"),
        _c("#E6E6FA", "Lavender", "OPI Do You Lilac It"),
        _c("#DDA0DD", "Plum Pastel", "Essie Go Ginza"),
        _c("#6A0DAD", "Royal Purple", "OPI Lincoln Park"),
        _c("#C8A2C8", "Lilac", "Essie Lilacism"),
        _c("#B57EDC", "Amethyst", "OPI Significant Other Color"),
        _c("#9F00FF", "Electric Violet", "Essie Sexy Divide"),
    ]},
    {"group": "Blues", "colors": [
        _c("#003087", "Navy", "OPI Russian Navy"),
        _c("#191970", "Midnight", "Essie Navigate Her"),
        _c("#0000FF", "Electric Blue", "OPI Fearlessly Alice"),
        _c("#1E90FF", "Cobalt", "Essie Butler Please"),
        _c("#4682B4", "Steel Blue", "OPI Bay Area Blue"),
        _c("#87CEEB", "Sky Blue", "Essie Find Me An Oasis"),
        _c("#4169E1", "Royal Blue", "OPI Your Royal Shyness"),
        _c("#008080", "Mermaid Teal", "Essie Teal"),
        _c("#20B2AA", "Light Teal", "OPI Teal The Cows Come Home"),
        _c("#77BFC7", "Aurora Blue", "OPI Fly"),
    ]},
    {"group": "Greens", "colors": [
        _c("#39FF14", "Neon Green", "Essie Neon Lights"),
        _c("#228B22", "Forest Green", "OPI Stay Off The Lawn"),
        _c("#556B2F", "Olive", "Essie Olive My Life"),
        _c("#9CAF88", "Sage", "Essie Sage To The Top"),
        _c("#50C878", "Emerald", "OPI Emerald Illusion"),
        _c("#8FBC8F", "Mint", "OPI Mint Candy Apple"),
        _c("#006400", "Dark Green", "OPI Stay Off The Lawn"),
        _c("#B7C795", "Pistachio", "Essie Chillato"),
    ]},
    {"group": "Darks", "colors": [
        _c("#0A0A0A", "Jet Black", "OPI Black Onyx"),
        _c("#2C3539", "Gunmetal", "Essie Smokin Hot"),
        _c("#3D0C02", "Dark Cherry", "OPI Vampsterdam"),
        _c("#1C1C1C", "Liquorice", "Essie Liquorice"),
        _c("#36454F", "Charcoal", "OPI Steel Waters"),
        _c("#4A4A4A", "Slate", "Essie Gel Couture"),
    ]},
    {"group": "Metallics", "colors": [
        _c("#B76E79", "Rose Gold", "OPI Be There In A Prosecco"),
        _c("#C0C0C0", "Silver Chrome", "OPI Steel Me The Show"),
        _c("#FFD700", "Gold Chrome", "OPI Glitter Gold"),
        _c("#CD7F32", "Bronze", "Essie Penny Talk"),
        _c("#E5E4E2", "Platinum", "OPI Platinum Card"),
        _c("#D4AF37", "Antique Gold", "OPI Glitter Gold"),
        _c("#8C7853", "Rose Bronze", "Essie Leading Lady"),
        _c("#B8860B", "Champagne Gold", "OPI Press Pass"),
    ]},
    {"group": "Trendy", "colors": [
        _c("#FFFAA0", "Butter Yellow", "Essie Baguette Me Not"),
        _c("#FFE8EE", "Glazed Donut", "OPI Bubble Bath"),
        _c("#E8E8FF", "Holographic", "OPI Glitter Off"),
        _c("#FFB7C5", "Coquette Pink", "OPI Passion"),
        _c("#F7CAC9", "Rose Quartz", "OPI Let Me Bayou A Drink"),
        _c("#FF6EC7", "Y2K Pink", "Essie Crush On You"),
        _c("#8B0000", "Mob Wife", "OPI Vampsterdam"),
        _c("#967259", "Latte Brown", "Essie Mochachino"),
        _c("#E8DCC8", "Oat Milk", "Essie Pillow Talk"),
        _c("#D4C5B0", "Quiet Luxury", "OPI Don't Pretzel"),
    ]},
]


# ---------------------------------------------------------------------------
# SIMPLIFIED STYLE GROUPINGS — map existing 60-style library into 5 groups
# ---------------------------------------------------------------------------

STYLE_GROUPS = [
    {
        "id": "popular",
        "label": "Most Popular",
        "style_ids": [
            "classic-gel", "glazed-donut", "french-classic", "chrome",
            "ombre-classic", "matte-gel",
        ],
        "badge": "Most Popular",
    },
    {
        "id": "nail-art",
        "label": "Nail Art",
        "style_ids": [
            "floral-art", "abstract-art", "geometric", "marble",
            "animal-print", "plaid", "swirl-art", "celestial",
        ],
    },
    {
        "id": "french",
        "label": "French Styles",
        "style_ids": [
            "french-classic", "french-colored", "french-ombre", "french-chrome",
            "glitter-ombre", "french-micro",
        ],
    },
    {
        "id": "special",
        "label": "Special Effects",
        "style_ids": [
            "mirror-powder", "holographic", "cat-eye", "iridescent",
            "aura-nails", "glitter-ombre",
        ],
    },
    {
        "id": "embellishments",
        "label": "Embellishments",
        "style_ids": [
            "rhinestone", "pearl-accents", "gold-foil", "3d-art",
        ],
    },
]
