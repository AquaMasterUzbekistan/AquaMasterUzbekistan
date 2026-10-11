"""Seed script for Tropheops sp. 'Chilumba Orange'."""

import sqlite3

def seed():
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    existing = cur.execute(
        "SELECT id FROM species WHERE scientific_name = ?",
        ("Tropheops sp. 'Chilumba Orange'",)
    ).fetchone()

    if existing:
        print(f"Tropheops sp. 'Chilumba Orange' already exists (id={existing[0]})")
        conn.close()
        return

    cur.execute("""
        INSERT INTO species (
            scientific_name, genus_id, author, year_described, origin_type, water_type,
            max_size_cm, body_shape, coloration, sexual_dimorphism, temp_min, temp_max,
            ph_min, ph_max, gh_min, gh_max, kh_min, kh_max, min_tank_liters,
            recommended_tank_liters, group_size_min, group_size_recommended, aggression,
            difficulty, diet_description, diet_plant, diet_protein, breeding_type,
            breeding_description, fry_care, male_description, female_description,
            genetics_info, color_morphs, wild_form, f_generation, natural_habitat,
            important_note, reliability, is_published, view_count, search_count,
            compare_count, taxonomic_status, conservation_status, depth_range,
            dietary_category, temperament, conspecific_aggression, interspecific_aggression,
            tank_setup_notes, filtration_notes, water_changes_notes, taxonomic_notes,
            evidence_quality_note, last_verified_date
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?
        )
    """, (
        "Tropheops sp. 'Chilumba Orange'", 56, "Konings", 1990, "wild", "freshwater",
        13.0, "Cho'ziq, kuchli muskulli mbuna shakli", "Olovrang dorsal suzgich, sarg'ish-moviy tana",
        "Erkaklar yorqin olovrang tusda, urg'ochilar xira jigarrang-sarg'ish", 24.0, 28.0,
        7.8, 8.6, 10.0, 20.0, 8.0, 14.0, 250,
        300, 5, "1 erkak va 3-4 urg'ochi (garem)", "aggressive",
        "intermediate", "Aufwuchs va qoyalardagi bir hujayrali suv o'tlari bilan oziqlanadi.",
        "Spirulina, o'simlikli granulalar, nori suv o'ti", "Mayda siklop, dafniya (cheklangan miqdorda)",
        "mouthbrooder", "Maternal mouthbrooder — urg'ochi tuxumlarni og'zida 21-25 kun davomida saqlaydi.",
        "Chavoqlar og'izdan chiqqach, yangi chiqqan artemiya naupliyalari va maydalangan spirulina bilan boqiladi.",
        "Erkaklarda yorqin olovrang tus, anal suzgichida sariq tuxum dog'lari (egg spots) mavjud.",
        "Urg'ochilar nisbatan kamtarona rangda, kamroq tajovuzkor.",
        "Malavi qoyali mbunasi, hududiy genetik xilma-xillik yuqori.",
        "Chilumba Orange, Mpanga Red, Luwino Blue", "Tabiiy yovvoyi populyatsiya", "F0 / F1",
        "Malavi ko'lining shimoliy qismidagi Chilumba qoyali biotopi (Chilumba Rocks). Chuqurlik: 3-15 m.",
        "Ovqat hazm qilish tizimi nozik (o'txo'r). Hayvoniy oqsil (motil, tubifex) berish qat'iyan taqiqlanadi (Malawi Bloat xavfi).",
        "scientific", 1, 0, 0,
        0, "Valid provisional taxon", "LC (Least Concern)", "3–15 m",
        "Herbivorous (Aufwuchs Grazer)", "Hududiy va g'ayratli", "Turdoshlariga nisbatan kuchli agressiv",
        "Boshqa tez suzuvchi Malavi mbunalari bilan yaxshi chiqishadi",
        "Ko'plab tosh boshpanalari, g'orlar va qumli grunt zarur.",
        "Kuchli biologik va mexanik filtratsiya, yaxshi kislorod ta'minoti.",
        "Haftada bir marta 25-30% suv yangilanishi lozim.",
        "Tropheops avlodining Chilumba qoyalariga xos bo'lgan geografik morfi.",
        "🟢 Ilmiy manba bilan tasdiqlangan (Konings: Malawi Cichlids in their Natural Habitat)",
        "2026-10-12"
    ))

    species_id = cur.lastrowid
    print(f"Inserted Tropheops sp. 'Chilumba Orange' (id={species_id})")

    # Subcategory
    cur.execute("INSERT OR IGNORE INTO species_categories (species_id, subcategory_id) VALUES (?, ?)", (species_id, 1))

    # Common names
    cur.execute("INSERT OR IGNORE INTO common_names (species_id, name, language) VALUES (?, ?, ?)", (species_id, "Trofeops Chilumba Olovrang", "uz"))
    cur.execute("INSERT OR IGNORE INTO common_names (species_id, name, language) VALUES (?, ?, ?)", (species_id, "Tropheops Chilumba Orange", "en"))
    cur.execute("INSERT OR IGNORE INTO common_names (species_id, name, language) VALUES (?, ?, ?)", (species_id, "Трофеопс Чилумба Оранж", "ru"))

    # Trade names
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (?, ?)", (species_id, "Tropheops Chilumba Orange"))
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (?, ?)", (species_id, "Tropheops sp. Chilumba"))
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (?, ?)", (species_id, "Chilumba Orange Mbuna"))

    # Locality
    loc = cur.execute("SELECT id FROM localities WHERE name = ?", ("Chilumba Rocks",)).fetchone()
    if loc:
        cur.execute("INSERT OR IGNORE INTO species_localities (species_id, locality_id) VALUES (?, ?)", (species_id, loc[0]))

    # Image
    cur.execute("""
        INSERT OR IGNORE INTO species_images (
            species_id, image_url, image_type, caption, source, verification
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        species_id,
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Pseudotropheus_demasoni.jpg/800px-Pseudotropheus_demasoni.jpg",
        "main",
        "Tropheops sp. 'Chilumba Orange' — erkak baliq",
        "Malawi.si / Cichlid-forum",
        "verified"
    ))

    # Also add "Ancistrus L144" and "L144" to trade_names for species 25 (Ancistrus cirrhosus)
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (25, 'Ancistrus L144')")
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (25, 'L144')")
    cur.execute("INSERT OR IGNORE INTO trade_names (species_id, name) VALUES (25, 'L144 Ancistrus')")

    conn.commit()
    conn.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
