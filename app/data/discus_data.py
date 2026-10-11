"""Dedicated Authoritative Discus (Symphysodon) Database.

Covers:
- Accepted scientific species (Symphysodon discus, S. aequifasciatus, S. tarzoo, S. haraldi)
- Taxonomic agreements and disputes (Ready et al. 2006 vs Bleher 2006 vs FishBase)
- Documented natural wild populations & geographical forms (Rio Negro, Tefé, Alenquer, Rio Madeira)
- Captive-bred strains & commercial colour varieties (Pigeon Blood, Snake Skin, Blue Diamond, etc.)
- Breeding history: Dr. Eduard Schmidt-Focke, Jack Wattley, Kitti Phanaitnorrachart
- Explicit distinction between biological taxa and commercial names
Sources: FishBase.org, Eschmeyer's Catalog of Fishes, SeriouslyFish.com, Ready et al. (2006), Bleher (2006).
"""

from __future__ import annotations

DISCUS_GENERA = [
    {
        "scientific_name": "Symphysodon",
        "author": "Heckel",
        "year_described": 1840,
        "subfamily": "Cichlinae",
        "family": "Cichlidae",
        "common_name": "Diskus (Disk baliq)",
        "description": (
            "Amazonka havzasining disk shaklidagi, nihoyatda salobatli va farengeal mukus bilan "
            "o'z chavoqlarini boquvchi qirol cichlidasi. Taksonomiyasi bo'yicha ilmiy bahslar mavjud."
        ),
    }
]

DISCUS_SPECIES = [
    {
        "scientific_name": "Symphysodon discus",
        "genus": "Symphysodon",
        "author": "Heckel",
        "year_described": 1840,
        "subcategory": "Discus",
        "common_names": [
            ("Xekkel diskusi", "uz"),
            ("Heckel Discus / Red Discus", "en"),
            ("Дискус Хеккеля", "ru"),
        ],
        "synonyms": [
            "Symphysodon discus discus Heckel, 1840",
            "Symphysodon discus willischwartzi Burgess, 1981",
        ],
        "trade_names": [
            "Heckel Discus",
            "Rio Negro Heckel",
            "Blue-headed Heckel",
            "Abacaxis Heckel",
        ],
        "origin_type": "wild",
        "max_size_cm": 20.0,
        "temp_min": 28.5,
        "temp_max": 32.0,
        "ph_min": 4.0,
        "ph_max": 5.5,
        "gh_min": 1.0,
        "gh_max": 4.0,
        "kh_min": 0.5,
        "kh_max": 2.0,
        "min_tank_liters": 300,
        "recommended_tank_liters": 450,
        "group_size_min": 6,
        "group_size_recommended": "Kamida 6-8 ta baliqdan iborat suruv",
        "aggression": "peaceful",
        "difficulty": "expert",
        "diet_description": (
            "Karnivor/omnivor: detrit, zooplankton, suv hasharotlari lichinkalari, "
            "yuqori sifatli granulalar, artemiya, dafniya. Oqsil va vitamin balansi juda muhim."
        ),
        "diet_plant": "Spirulina va detrit komponentlari",
        "diet_protein": "Artemiya, dafniya, maxsus toza diskus patesi",
        "dietary_category": "Omnivorous / Micropredator",
        "temperament": "Juda tinch, bosiq, suruvchi va tortinchoq",
        "conspecific_aggression": (
            "Gala ichida iyerarxiya o'rnatish uchun engil turtishishlar bo'ladi; "
            "yakka saqlansa stressga tushadi, 6 tadan kam bo'lsa kuchsizi quvg'inga uchraydi."
        ),
        "interspecific_aggression": "Boshqa barcha tinch baliqlarga mutlaqo zararsiz.",
        "tank_setup_notes": (
            "Yumshoq kislotali qora suv (blackwater), torf ekstrakti, barglar (Catappa), "
            "nozik vertikal daraxt ildizlari (driftwood), mayin daryo qumi va xira yorug'lik."
        ),
        "filtration_notes": "Katta hajmli tashqi biofiltr, o'ta toza suv, past oqim tezligi.",
        "water_changes_notes": "Haftasiga 2 marta 25-35% yumshoq osmos suvi bilan almashtirish.",
        "taxonomic_notes": (
            "Heckel tomonidan 1840 yilda tasvirlangan ilk tipik diskus turi. "
            "Tananing 1-, 5- (markaziy) va 9-vertikal chiziqlari boshqalarga qaraganda ancha keng va to'q "
            "bo'lib, 'Heckel bar' deb ataladi. Burgess (1981) Rio Abacaxis populyatsiyasini "
            "S. discus willischwartzi deb kichik turga ajratgan."
        ),
        "evidence_quality_note": "🟢 Ilmiy manba bilan tasdiqlangan (Heckel 1840, Ready et al. 2006).",
        "last_verified_date": "2026-10-10",
        "breeding_type": "substrate_spawner",
        "breeding_description": (
            "Vertikal silliq yuzaga (yog'och, keramika konusi) tuxum qo'yadi. Tuxumlar 50-60 soatda "
            "ochiladi. Eng noyob biologik xususiyati: chavoqlar erkin suza boshlagach (3-kuni), "
            "ota-onasining tanasidagi ozuqaviy epidermal shilliq (mukus) bilan oziqlanadi."
        ),
        "fry_care": "Dastlabki 2-3 hafta faqat ota-ona shilliqi, keyin yangi chiqqan artemiya naupliyelari.",
        "male_description": "Kattaroq tana, orqa va anal suzgich uchlari cho'zilgan, peshonasi qalinroq.",
        "female_description": "Biroz kichikroq, yumaloqroq anal suzgich.",
        "genetics_info": (
            "Wild Heckel diskuslari genetik jihatdan eng qadimiy bazal tarmoq hisoblanadi. "
            "Boshqa diskuslar bilan chatishganda F1 avlodda Heckel markaziy chizig'i qisman saqlanadi."
        ),
        "color_morphs": "Tabiiy: Rio Negro ko'k boshli, Abacaxis ko'k-qizil yo'lli.",
        "wild_form": "Markaziy to'q qora 5-chiziq (Heckel bar), zangori-ko'k ingichka chiziqchalar.",
        "natural_habitat": "Rio Negro havzasining chuqur, sekin oquvchi qora suvlari, suv bosgan o'rmonlar.",
        "conservation_status": "LC (FishBase / IUCN)",
        "depth_range": "1.5–5 m",
        "locality": {
            "name": "Rio Negro (Anavilhanas arxipelagi)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -2.600,
            "longitude": -60.800,
            "habitat": "Kislotali qora suv, torf va chirigan o'tinlar to'plangan qirg'oq zonalari.",
            "description": "Heckel diskusining klassik tabiiy areali; suv o'ta kislotali va yumshoq."
        },
        "sources": [
            "FishBase.org (Symphysodon discus)",
            "Eschmeyer's Catalog of Fishes (Heckel 1840)",
            "SeriouslyFish.com (Symphysodon discus)",
            "Ready, Ferreira & Kullander (2006) J. Fish Biol.",
        ],
    },
    {
        "scientific_name": "Symphysodon aequifasciatus",
        "genus": "Symphysodon",
        "author": "Pellegrin",
        "year_described": 1904,
        "subcategory": "Discus",
        "common_names": [
            ("Yashil va jigarrang diskus", "uz"),
            ("Green Discus / Brown Discus", "en"),
            ("Зеленый / коричневый дискус", "ru"),
        ],
        "synonyms": [
            "Symphysodon discus aequifasciatus Pellegrin, 1904",
            "Symphysodon aequifasciata axelrodi Schultz, 1960 (Brown Discus)",
        ],
        "trade_names": [
            "Green Discus",
            "Brown Discus",
            "Alenquer Discus",
            "Santarem Brown",
            "Tefe Green",
        ],
        "origin_type": "wild",
        "max_size_cm": 18.0,
        "temp_min": 27.0,
        "temp_max": 31.0,
        "ph_min": 5.2,
        "ph_max": 6.8,
        "gh_min": 2.0,
        "gh_max": 8.0,
        "kh_min": 1.0,
        "kh_max": 4.0,
        "min_tank_liters": 250,
        "recommended_tank_liters": 400,
        "group_size_min": 6,
        "group_size_recommended": "6-10 ta diskus",
        "aggression": "peaceful",
        "difficulty": "intermediate",
        "diet_description": "Yuqori oqsilli sifatli granulalar, artemiya, mysis, spirulina, toza diskus aralashmasi.",
        "diet_plant": "O'simlikli qo'shimchalar, spirulina",
        "diet_protein": "Artemiya, qon qurti (muzlatilgan), maxsus diskus mix",
        "dietary_category": "Omnivorous",
        "temperament": "Tinch, guruhda yashovchi, ijtimoiy",
        "conspecific_aggression": "Guruhda yengil pozitsiya kurashi; 6 tadan ko'p bo'lsa tarqaladi.",
        "interspecific_aggression": "Boshqa baliqlarga mutlaqo tinch.",
        "tank_setup_notes": "Keng suzish maydoni, vertikal shoxlar, mayin qum, toza filtrlangan suv.",
        "filtration_notes": "Kuchli biologik filtratsiya va past oqim.",
        "water_changes_notes": "Haftalik 30-40% toza yumshoq suv.",
        "taxonomic_notes": (
            "Pellegrin (1904) tomonidan tasvirlangan. 9 ta teng kenglikdagi vertikal yo'llarga ega "
            "('aequifasciatus' = teng yo'lli degan ma'noni anglatadi). Tarixiy jihatdan yashil (aequifasciatus) "
            "va jigarrang (axelrodi) kabi formalarga bo'lingan. Hozirgi kunda markaziy va sharqiy Amazonka "
            "populyatsiyalarini o'z ichiga oladi."
        ),
        "evidence_quality_note": "🟢 Ilmiy manba bilan tasdiqlangan (FishBase, Pellegrin 1904).",
        "last_verified_date": "2026-10-10",
        "breeding_type": "substrate_spawner",
        "breeding_description": (
            "Monogam juftlik vertikal tekis yuzalarga 150-350 ta tuxum qo'yadi. "
            "Ikkala ota-ona ham tuxum ustida yelpig'ich harakatlari qiladi va chavoqlarni "
            "tana shilliqi bilan oziqlantiradi."
        ),
        "fry_care": "Mukus bilan boqish, 5-kundan mikro artemiya.",
        "male_description": "Peshonasi kattaroq, orqa suzgich uchi uzunroq.",
        "female_description": "Bir oz ixchamroq, qorin qismi tuxum qo'yishda to'liq.",
        "genetics_info": (
            "Ushbu tur akvariumchilikdagi deyarli barcha zamonaviy selektsion diskus liniyalarining "
            "(Turquoise, Red, Pigeon Blood) asosiy genetik zaminini tashkil etadi."
        ),
        "color_morphs": "Yashil Tefe shakli, Alenquer qizil-jigarrang shakli, Santarem jigarrang shakli.",
        "wild_form": "9 ta teng qora yo'l, qizil yoki sarg'ish-jigarrang tana, moviy to'lqinsimon chiziqlar.",
        "natural_habitat": "Amazonka daryosining o'rta va quyi oqimi, Rio Solimões, Lake Tefé.",
        "conservation_status": "LC (IUCN / FishBase)",
        "depth_range": "1.0–4.0 m",
        "locality": {
            "name": "Alenquer (Pará shtati)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -1.940,
            "longitude": -54.740,
            "habitat": "Toza daryo qirg'og'idagi sokin ko'rfazlar va suv bosgan o'rmonlar.",
            "description": "Mashhur Alenquer qizil diskuslari vatani; qizg'ish tana rangi bilan mashhur."
        },
        "sources": [
            "FishBase.org (Symphysodon aequifasciatus)",
            "Eschmeyer's Catalog of Fishes (Pellegrin 1904)",
            "SeriouslyFish.com",
            "Bleher, H. (2006) Bleher's Discus Vol 1",
        ],
    },
    {
        "scientific_name": "Symphysodon tarzoo",
        "genus": "Symphysodon",
        "author": "Lyons",
        "year_described": 1959,
        "subcategory": "Discus",
        "common_names": [
            ("Qizil dog'li yashil diskus", "uz"),
            ("Western Blue/Green Discus", "en"),
            ("Западный зеленый дискус (Тарзу)", "ru"),
        ],
        "synonyms": [
            "Symphysodon aequifasciata tarzoo Lyons, 1959",
            "Symphysodon discus tarzoo Lyons, 1959",
        ],
        "trade_names": [
            "Red Spotted Green (RSG)",
            "Tefe Royal Green",
            "Nanay Green Discus",
            "Japura Green",
        ],
        "origin_type": "wild",
        "max_size_cm": 17.5,
        "temp_min": 27.5,
        "temp_max": 31.5,
        "ph_min": 5.0,
        "ph_max": 6.5,
        "gh_min": 1.0,
        "gh_max": 5.0,
        "kh_min": 1.0,
        "kh_max": 3.0,
        "min_tank_liters": 250,
        "recommended_tank_liters": 400,
        "group_size_min": 6,
        "group_size_recommended": "Kamida 6 ta diskus",
        "aggression": "peaceful",
        "difficulty": "advanced",
        "diet_description": "Yuqori sifatli oqsil granulalari, artemiya, dafniya, maxsus toza bio-ozuqa.",
        "diet_plant": "Spirulina va detrit",
        "diet_protein": "Artemiya, dafniya, mol yuragi patesi",
        "dietary_category": "Omnivorous",
        "temperament": "Tinch va olijanob",
        "conspecific_aggression": "Suruv iyerarxiyasida yengil turtishishlar, zararsiz.",
        "interspecific_aggression": "Tinch kichik tetralar va koridoraslar bilan ideal.",
        "tank_setup_notes": "Amazonka biotopi: nozik qum, daraxt shoxlari, xira yorug'lik, barglar.",
        "filtration_notes": "Sokin oqimli quvvatli tashqi kanistr filtr.",
        "water_changes_notes": "Haftada 30-40% osmos/toza suv.",
        "taxonomic_notes": (
            "Lyons (1959) tomonidan kashf etilgan va Ready, Ferreira & Kullander (2006) tomonidan "
            "alohida biologik tur sifatida ilmiy qayta tasdiqlangan. Purus arkasining g'arbidagi "
            "(Peru, Kolumbiya va g'arbiy Braziliya) populyatsiyalarni tashkil qiladi. "
            "Tanasida va anal suzgichida aniq qizil nuqtalar (red spots) bo'lishi bilan boshqa diskuslardan farq qiladi."
        ),
        "evidence_quality_note": "🟢 Ilmiy manba bilan tasdiqlangan (Ready et al. 2006, Lyons 1959).",
        "last_verified_date": "2026-10-10",
        "breeding_type": "substrate_spawner",
        "breeding_description": (
            "Yumshoq kislotali suvda substratga tuxum qo'yadi; chavoqlarni epidermal shilliq bilan boqadi."
        ),
        "fry_care": "Ota-ona shilliqi va 5-kundan yangi chiqqan artemiya.",
        "male_description": "Tanasida va anal suzgichida kuchli qizil nuqtalar to'plami, yorqinroq moviy chiziqlar.",
        "female_description": "Biroz kamroq qizil nuqtali, yumaloqroq shakl.",
        "genetics_info": (
            "Mitoxondriyal DNK tahlillari S. tarzoo sharqiy diskuslardan (S. aequifasciatus va S. haraldi) "
            "genetik jihatdan tubdan farq qilishini ko'rsatgan (Ready et al. 2006)."
        ),
        "color_morphs": "Tefe Green, Nanay Green, Jurua Green.",
        "wild_form": "Zangori-yashil tana fonida qizil nuqtalar va qora vertikal yo'llar.",
        "natural_habitat": "G'arbiy Amazonka, Rio Nanay, Rio Japura, Tefé ko'li yuqori qismi.",
        "conservation_status": "LC",
        "depth_range": "1.0–3.5 m",
        "locality": {
            "name": "Tefé ko'li (Amazonas shtati)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -3.360,
            "longitude": -64.710,
            "habitat": "Sayoz o'rmon ko'llari va quyilish tarmoqlari.",
            "description": "Mashhur Royal Green va Red Spotted Green diskuslari vatani."
        },
        "sources": [
            "Ready, Ferreira & Kullander (2006) J. Fish Biol. 69:200-211",
            "FishBase.org (Symphysodon tarzoo)",
            "Eschmeyer's Catalog of Fishes (Lyons 1959)",
        ],
    },
    {
        "scientific_name": "Symphysodon haraldi",
        "genus": "Symphysodon",
        "author": "Schultz",
        "year_described": 1960,
        "subcategory": "Discus",
        "common_names": [
            ("Xarald moviy diskusi", "uz"),
            ("Harald's Blue/Brown Discus", "en"),
            ("Дискус Харальда", "ru"),
        ],
        "synonyms": [
            "Symphysodon aequifasciata haraldi Schultz, 1960",
            "Symphysodon aequifasciata axelrodi Schultz, 1960",
        ],
        "trade_names": [
            "Blue Discus",
            "Royal Blue",
            "Madeira Blue",
            "Tapajos Discus",
        ],
        "origin_type": "wild",
        "max_size_cm": 18.0,
        "temp_min": 27.5,
        "temp_max": 31.0,
        "ph_min": 5.5,
        "ph_max": 7.0,
        "gh_min": 2.0,
        "gh_max": 8.0,
        "kh_min": 1.0,
        "kh_max": 4.0,
        "min_tank_liters": 250,
        "recommended_tank_liters": 400,
        "group_size_min": 6,
        "group_size_recommended": "Kamida 6 ta diskus",
        "aggression": "peaceful",
        "difficulty": "intermediate",
        "diet_description": "Sifatli quruq granulalar, artemiya, dafniya, diskus patelari.",
        "diet_plant": "Spirulina komponentlari",
        "diet_protein": "Artemiya, dafniya, qurt lichinkalari",
        "dietary_category": "Omnivorous",
        "temperament": "Tinch, do'stona, suruvchi",
        "conspecific_aggression": "Tinch iyerarxiya",
        "interspecific_aggression": "Mutlaqo tinch",
        "tank_setup_notes": "Biotop akvarium: vertikal novdalar, mayin oq qum, o'simliklar.",
        "filtration_notes": "Yuqori darajadagi bio-filtratsiya.",
        "water_changes_notes": "Haftalik 30-40% suv almashtirish.",
        "taxonomic_notes": (
            "Schultz (1960) tomonidan tasvirlangan. Ready, Ferreira & Kullander (2006) uni alohida "
            "tur deb qabul qilgan, biroq Heiko Bleher (2006) va FishBase uni S. aequifasciatus turning "
            "kichik sinonimi deb hisoblaydi. Bu taksonomik ixtilof ilmiy adabiyotlarda faol muhokama qilinadi."
        ),
        "evidence_quality_note": "🟡 Ishonchli manbada qayd etilgan, lekin taksonomik maqomi bahsli.",
        "last_verified_date": "2026-10-10",
        "breeding_type": "substrate_spawner",
        "breeding_description": "Tekis substratga tuxum qo'yadi, ota-ona shilliqi bilan chavoqlarni boqadi.",
        "fry_care": "Epidermal mukus va artemiya.",
        "male_description": "To'liq ko'k vertikal to'lqinlar (Royal Blue formasi), yirik tana.",
        "female_description": "Biroz kamroq zangori chiziqlar.",
        "genetics_info": "Brilliant Turquoise va Cobalt Blue kabi akvarium durdonalarining boshlang'ich ajdodi.",
        "color_morphs": "Royal Blue, Semi-Royal, Solid Brown.",
        "wild_form": "Jigarrang fonda kuchli yaltiroq feruza-ko'k to'lqinlar.",
        "natural_habitat": "Sharqiy Amazonka, Rio Tapajós, Rio Madeira quyi oqimi.",
        "conservation_status": "LC",
        "depth_range": "1.0–3.0 m",
        "locality": {
            "name": "Rio Madeira (Borba hududi)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -4.390,
            "longitude": -59.590,
            "habitat": "Loyqa va toza suvlar aralashmasi, sokin soylar.",
            "description": "Mashhur Moviy diskuslar (Blue Discus) populyatsiyasi areali."
        },
        "sources": [
            "Ready, Ferreira & Kullander (2006) J. Fish Biol.",
            "Schultz, L.P. (1960) Tropical Fish Hobbyist",
            "Bleher, H. (2006) Bleher's Discus Vol 1",
            "FishBase.org",
        ],
    },
]
