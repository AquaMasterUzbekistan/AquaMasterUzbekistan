"""Comprehensive Knowledge Base — 14 Essential Aquarium Guides (Section 8).

Written in clear, educational Uzbek with practical examples, calculations, and critical warnings.
"""

from __future__ import annotations

KNOWLEDGE_ARTICLES = [
    {
        "id": 1,
        "title": "1. Azot aylanishi va yangi akvariumni ishga tushirish",
        "category": "Gidrokimyo va Filtrlash",
        "emoji": "🔄",
        "summary": "Yangi akvariumni baliq qo'shishdan oldin to'g'ri biologik ishga tushirish (Fishless cycle).",
        "content": (
            "🔄 <b>AZOT AYLANISHI VA YANGI AKVARIUMNI ISHGA TUSHIRISH</b>\n\n"
            "Yangi akvariumga darhol baliq solish — boshlovchilarning 90% xatosidir! "
            "Suv shaffof bo'lib ko'ringani bilan, unda zaharli moddalarni parchalovchi foydali bakteriyalar koloniyasi hali mavjud bo'lmaydi.\n\n"
            "🔬 <b>Biologik azot aylanishi bosqichlari:</b>\n"
            "1. Baliq chiqindilari va ozuqa qoldiqlari o'ta zaharli <b>Ammiak (NH3)</b> ga aylanadi.\n"
            "2. <i>Nitrosomonas</i> bakteriyalari ammiakni iste'mol qilib, zaharli <b>Nitrit (NO2)</b> ga aylantiradi.\n"
            "3. <i>Nitrospira</i> va <i>Nitrobacter</i> bakteriyalari nitritni kamroq xavfli bo'lgan <b>Nitrat (NO3)</b> ga aylantiradi.\n"
            "4. Nitrat esa muntazam suv almashtirish orqali tizimdan chiqarib tashlanadi.\n\n"
            "⏳ <b>Akvariumni to'g'ri ishga tushirish tartibi:</b>\n"
            "• Grunt, toshlar va filtri o'rnatilib, xlori ketkazilgan suv quyiladi.\n"
            "• Filtr va kompressor 24/7 to'xtovsiz ishga tushiriladi.\n"
            "• Bakteriyalarni oziqlantirish uchun har 2 kunda ozgina ozuqa tashlab turiladi yoki tayyor bakteriya starteti qo'shiladi.\n"
            "• To'liq tsikl shakllanishi odatda <b>3 haftadan 5 haftagacha</b> davom etadi.\n"
            "• Faqat Ammiak=0 va Nitrit=0 bo'lgandagina dastlabki bir nechta baliqni kiritish mumkin."
        ),
    },
    {
        "id": 2,
        "title": "2. Ammiak, nitrit va nitrat: xavflar va nazorat",
        "category": "Gidrokimyo",
        "emoji": "☠️",
        "summary": "Akvariumdagi 3 asosiy azot birikmasining zaharlilik darajalari va xavfsiz chegaralari.",
        "content": (
            "☠️ <b>AMMIAK, NITRIT VA NITRAT: ZAHARLANISHNING OLDINI OLISH</b>\n\n"
            "Akvarium suvining shaffofligi uning tozaligini bildirmaydi. Ko'rinmas toksinlar baliqlar nobud bo'lishining bosh sababchisidir.\n\n"
            "1. <b>Ammiak (NH3 / NH4+):</b>\n"
            "• Xavfsiz darajasi: <b>0.00 mg/l</b>.\n"
            "• 0.25 mg/l dan oshsa — qon aylanishi buziladi, jabralar qizaradi, baliqlar yuzada havo yetishmasligidan entikadi.\n"
            "• Suv pH darajasi qancha yuqori (ishqoriy) bo'lsa, erkin NH3 shunchalik zaharliroq bo'ladi (Malavi va Tanganika akvariumlarida ayniqsa xavfli!).\n\n"
            "2. <b>Nitrit (NO2):</b>\n"
            "• Xavfsiz darajasi: <b>0.00 mg/l</b>.\n"
            "• Qondagi gemoglobinni metgemoglobinga aylantirib, qonning kislorod tashish qobiliyatini to'xtatadi («qo'ng'ir qon kasalligi»).\n\n"
            "3. <b>Nitrat (NO3):</b>\n"
            "• Xavfsiz darajasi: <b>&lt; 20-30 mg/l</b>.\n"
            "• 50 mg/l dan yuqorisi baliqlar o'sishini to'xtatadi, immunitetni tushiradi va jigar faoliyatini buzadi.\n\n"
            "🛠 <b>Zudlik bilan choralar:</b>\n"
            "Toksinlar oshib ketganda darhol 30-40% yangi xlorlanmagan suv bilan almashtiring va ovqatlantirishni 2 kunga to'xtating!"
        ),
    },
    {
        "id": 3,
        "title": "3. pH, GH va KH ko'rsatkichlari",
        "category": "Gidrokimyo",
        "emoji": "🧪",
        "summary": "Kislotalilik, umumiy qattiqlik va karbonat buferi tushunchalari.",
        "content": (
            "🧪 <b>pH, GH VA KH: SUV PARAMETRLARI VA BUFER TIZIMI</b>\n\n"
            "Har bir baliq turi o'z tabiiy yashash muhiti parametrlariga moslashgan.\n\n"
            "• <b>pH (Vodorod ko'rsatkichi):</b>\n"
            "Suvning kislotalilik yoki ishqoriylik darajasi (0–14 shkala). 7.0 — neytral.\n"
            "- Amazonka baliqlari (Diskus, Tetralar): pH 5.5–6.8 (kislotali va yumshoq).\n"
            "- Malavi va Viktoriya cichlidlari: pH 7.8–8.6 (ishqoriy).\n"
            "- Tanganika cichlidlari: pH 8.5–9.2 (kuchli ishqoriy).\n\n"
            "• <b>KH (Karbonat qattiqligi / Bufer):</b>\n"
            "Suvdagi gidrokarbonat ionlari miqdori. KH ning eng muhim vazifasi — <b>pH keskin qulashining (pH crash)</b> oldini oluvchi qalqon hisoblanadi. KH &gt; 6-8 bo'lsa, pH barqaror turadi.\n\n"
            "• <b>GH (Umumiy qattiqlik):</b>\n"
            "Suv tarkibidagi kaltsiy (Ca) va magniy (Mg) ionlari yig'indisi. Baliqlarning suyak va tangachalar rivojlanishi hamda osmoregulyatsiyasi uchun zarur.\n\n"
            "⚠️ <b>Ogohlantirish:</b> Baliqlar uchun parametrning mutlaq qiymatidan ko'ra, uning <b>barqarorligi</b> muhimroq. pH ni bir kunda 0.3 dan ortiq o'zgartirish baliqni pH-shok holatiga soladi!"
        ),
    },
    {
        "id": 4,
        "title": "4. Harorat va kislorod balansi",
        "category": "Parvarish",
        "emoji": "🌡️",
        "summary": "Suvdagi erigan kislorod miqdori va harorat o'rtasidagi teskari bog'liqlik.",
        "content": (
            "🌡️ <b>HARORAT VA KISLOROD BALANSI</b>\n\n"
            "Akvariumda suv harorati ko'tarilgan sari, unda erigan kislorod (O2) miqdori keskin kamayadi, baliqlarning moddalar almashinuvi esa tezlashib, kislorodga ehtiyoji 2 barobar ortadi!\n\n"
            "📊 <b>Optimal harorat diapazonlari:</b>\n"
            "• Afrika cichlidlari (Malawi, Tanganyika): 24–27 °C\n"
            "• Janubiy Amerika (Diskuslar): 28–30 °C\n"
            "• Umumiy tropik baliqlar (Guppi, Skalyariya, Neontetra): 23–26 °C\n"
            "• Oltin baliqlar (sovuq suvli): 18–22 °C\n\n"
            "💨 <b>Kislorod ta'minoti qoidalari:</b>\n"
            "• Kislorod suv tubidan chiqadigan pufakchalardan emas, asosan <b>suv sirtining to'lqinlanishi</b> orqali atmosferadan so'riladi.\n"
            "• Shuning uchun filtr oqimini suv yuzasini qimirlatib turadigan qilib o'rnatish lozim.\n"
            "• Yoz oylarida harorat 29-30 °C dan oshganda kompressor aeratsiyasini maksimal darajaga ko'tarish yoki suvni sovutish ventilyatori o'rnatish shart!"
        ),
    },
    {
        "id": 5,
        "title": "5. Mexanik, biologik va kimyoviy filtratsiya",
        "category": "Filtrlash",
        "emoji": "⚙️",
        "summary": "Akvarium filtratsiyasining uchta ustuni va ularning vazifalari.",
        "content": (
            "⚙️ <b>FILTRATSIYANING 3 TURI: TO'G'RI TIZIM QURISH</b>\n\n"
            "Akvarium barqarorligi uning filtri qanchalik to'g'ri ishlashiga bog'liq.\n\n"
            "1. <b>Mexanik filtratsiya:</b>\n"
            "Suvdagi ko'rinadigan qattiq zarralar, ozuqa qoldiqlari va najasni tutib qoladi. Vositalar: gubkalar (parolon), sintepon. Ular ifloslanganda muntazam yuvib turilishi shart, aks holda ular organik chiqindilar omboriga aylanadi.\n\n"
            "2. <b>Biologik filtratsiya (ENG MUHIMI):</b>\n"
            "Foydali nitrifikatsiyalovchi bakteriyalar uchun g'ovakli uy vazifasini bajaradi. Vositalar: g'ovakli keramika halqalari (Ceramic rings), sinterlangan shisha (Seachem Matrix, Eheim Substrat Pro), lavali toshlar. Bu materiallar suv ostida hech qachon xlorli vodoprovod suvida yuvilmaydi!\n\n"
            "3. <b>Kimyoviy filtratsiya:</b>\n"
            "Molekulyar darajadagi moddalarni, dorilarni, sariq pigmentlarni va og'ir metallarni o'ziga yutadi. Vositalar: Faollashtirilgan ko'mir (Active Carbon), ion almashtiruvchi qatronlar (Purigen). Dori qo'llanilganda ko'mir filtrdan olinishi shart!"
        ),
    },
    {
        "id": 6,
        "title": "6. Filtr materiallari va ularni tozalash tartibi",
        "category": "Filtrlash",
        "emoji": "🧼",
        "summary": "Biologik bakteriyalarni o'ldirmasdan filtrni tozalash qoidalari.",
        "content": (
            "🧼 <b>FILTR MATERIALLARI VA ULARNI TOZALASH QOIDASI</b>\n\n"
            "Ko'p uchraydigan fojia: Egasi filtrni jo'mrakdagi sovuq yoki issiq suv ostida sovunlab yuvadi, oqibatda barcha foydali bakteriyalar o'lib, 2 kundan keyin ammiak portlashi yuz beradi!\n\n"
            "📌 <b>Oltin qoidalar:</b>\n"
            "1. <b>Faqat akvarium suvida yuvish:</b> Filtrni tozalash uchun chelakka akvariumdan suv olinadi va filtr gubkalari shu suvda yengil siqib chayiladi.\n"
            "2. <b>Jo'mrak suvidan xlor:</b> Shahar vodoprovod suvida erigan xlor bir necha soniyada barcha biologik koloniyani qirib tashlaydi.\n"
            "3. <b>Bir vaqtda hammasini almashtirmaslik:</b> Tashqi filtrda bir nechta korzina bo'lsa, barcha materiallar birdaniga almashtirilmaydi. Bir safar gubka yangilansa, keyingi oy keramika qisman yangilanadi.\n"
            "4. <b>Tozalash muddati:</b>\n"
            "• Ichki filtrlar (gubka): har 1–2 haftada bir marta.\n"
            "• Tashqi filtrlar (kanistr): har 2–4 oyda bir marta (oqim sezilarli susayganda)."
        ),
    },
    {
        "id": 7,
        "title": "7. Suv almashtirish qoidalari",
        "category": "Parvarish",
        "emoji": "🪣",
        "summary": "Suv almashtirish hajmi, tayyorlash va gruntni sifonlash.",
        "content": (
            "🪣 <b>MUNTAZAM SUV ALMASHTIRISH: SALOMATLIK GAROVI</b>\n\n"
            "Filtr har qancha kuchli bo'lmasin, u nitrat va fosfatlarni yo'qota olmaydi. Yagona tabiiy yo'l — suvni muntazam yangilab turishdir.\n\n"
            "📅 <b>Almashtirish hajmi va grafigi:</b>\n"
            "• Standart tropik akvariumlar: haftada bir marta <b>20–25%</b>.\n"
            "• Zich joylashgan Malavi/Tanganika cichlidlari: haftada bir marta <b>30–35%</b>.\n"
            "• Chavoqlar boqiladigan idishlar: har 1–2 kunda <b>20–50%</b>.\n\n"
            "⚠️ <b>Hech qachon suvni 100% to'liq almashtirmang!</b> Bu butun biosferani ag'dar-to'ntar qilib, baliqlarni stress va kasallikka yetaklaydi.\n\n"
            "🚰 <b>Quyiladigan suvga talablar:</b>\n"
            "• Harorat farqi: yangi suv akvariumdagi suvdan ko'pi bilan ±1-2 °C farq qilishi kerak.\n"
            "• Xlorsizlantirish: Suv kamida 24 soat tindiriladi yoki maxsus sifatli deklorinator (masalan, Seachem Prime, Tetra AquaSafe) qo'shiladi.\n"
            "• Grunt sifoni: Har 2 haftada grunt tubidagi najas va qoldiqlar sifon yordamida tortib olinadi."
        ),
    },
    {
        "id": 8,
        "title": "8. Oziqlantirish va ratsion balansi",
        "category": "Oziqlantirish",
        "emoji": "🥗",
        "summary": "O'txo'r va yirtqich baliqlarni to'g'ri oziqlantirish, Malawi Bloat xavfi.",
        "content": (
            "🥗 <b>OZIQLANTIRISH VA RATSION BALANSI</b>\n\n"
            "Akvariumda baliqlarning ochlikdan o'lishi deyarli uchramaydi, ammo <b>ortiqcha ovqatlantirish (overfeeding)</b> oqibatida o'lishi har kuni sodir bo'ladi!\n\n"
            "⏱ <b>Asosiy qoidalar:</b>\n"
            "1. <b>2–3 daqiqa qoidasi:</b> Baliqlarga shunchalik miqdorda ozuqa berilishi kerakki, ular barchasini 2 daqiqada yeb tugatsin. Tubga cho'kib qolgan ozuqa suvni buzadi.\n"
            "2. <b>Chastota:</b> Katta yoshdagi baliqlarga kuniga 1 yoki 2 marta oz-ozdan beriladi. Haftada 1 kun ochlik kuni (fasting day) e'lon qilish oshqozon-ichak yo'lini tozalaydi.\n\n"
            "🚫 <b>MALAWI BLOAT — O'txo'r baliqlar xavfi:</b>\n"
            "• Mbuna guruhidagi baliqlar (Demasoni, Pseudotropheus, Tropheus) tabiiy o'txo'r bo'lib, uzun ichakka ega.\n"
            "• Ularga hayvoniy yog'li ozuqa (motil, trubochnik, yurak qiymasi) berilsa, ichak tutiladi, qorin shishadi va o'limga olib keladi (Bloat).\n"
            "• Mbunalarga faqat spirulina, o'simlikli granulalar va sabzavotlar berilishi shart!"
        ),
    },
    {
        "id": 9,
        "title": "9. Kasallik belgilari va profilaktika",
        "category": "Salomatlik",
        "emoji": "🩺",
        "summary": "Oqqo'tir (Ich), suzgich chirishi, geksamitoz va profilaktika choralari.",
        "content": (
            "🩺 <b>KASALLIK BELGILARI VA PROFILAKTIKA</b>\n\n"
            "Akvariumda kasallikning 95% sababi — noto'g'ri suv sharoiti va stress natijasida immunitetning pasayishidir. Infeksiya qo'zg'atuvchilari har qanday akvariumda uxlab yotadi.\n\n"
            "🚩 <b>Xavfli belgilar:</b>\n"
            "• Baliq toshlar va dekoratsiyalarga tanasini ishqalay boshlaydi (parazit belgisi).\n"
            "• Suzgichlarini qisib, burchakda yoki suv yuzasida sust turadi.\n"
            "• Tanasida oq manna yormasiga o'xshash donachalar paydo bo'ladi — <b>Ixtioftirioz (Oqqo'tir / Ich)</b>.\n"
            "• Axlat oq va shilliq ip kabi chiqadi — <b>Geksamitoz / Ichak flagellatlari</b>.\n"
            "• Ko'zlari bo'rtib chiqadi (Popeye) yoki tangachalari qarag'ay qubbasidek hurpayadi (Dropsy / Istisqo).\n\n"
            "🛡 <b>Profilaktika:</b>\n"
            "Muntazam suv almashtirish, to'g'ri harorat va sifatli ozuqa — eng zo'r doridan ham samaraliroqdir!"
        ),
    },
    {
        "id": 10,
        "title": "10. Karantin va yangi baliqlarni moslashtirish",
        "category": "Salomatlik",
        "emoji": "🛡️",
        "summary": "Tomchilab moslashtirish (Drip acclimation) va 3 haftalik karantin qoidalari.",
        "content": (
            "🛡️ <b>KARANTIN VA YANGI BALIQLARNI MOSLASHTIRISH</b>\n\n"
            "Do'kondan yoki bozordan sotib olingan yangi baliqni darhol umumiy akvariumga qo'yib yuborish — butun baliqlar oilasiga o'lim hukmi bo'lishi mumkin!\n\n"
            "1. <b>Karantin idishi (Quarantine tank):</b>\n"
            "• Alohida 20-40 litrli shisha idish, oddiy gubkali filtr va isitgich bilan jihozlanadi.\n"
            "• Yangi keltirilgan baliq kamida <b>2–3 hafta</b> ushbu idishda kuzatiladi.\n"
            "• Yashirin parazit yoki infeksiya belgilari bo'lsa, umumiy akvariumni zaharlamasdan davolanadi.\n\n"
            "2. <b>Tomchilab moslashtirish (Drip acclimation):</b>\n"
            "• Xaltadagi suv bilan akvariumdagi suvning harorati va pH ko'rsatkichi har xil bo'ladi.\n"
            "• Xalta ochilib, 20 daqiqa akvarium yuzasida suzdiriladi (harorat tenglashishi uchun).\n"
            "• So'ngra xaltaga har 5 daqiqada akvariumdan oz-ozdan suv quyilib, parametrlar 40 daqiqa davomida tenglashtiriladi.\n"
            "• <b>Muhim:</b> Do'kon suvi akvariumga quyilmaydi, baliq to'r (sachok) bilan olinib o'tkaziladi!"
        ),
    },
    {
        "id": 11,
        "title": "11. Ko‘paytirish va chavoq parvarishi",
        "category": "Ko'paytirish",
        "emoji": "🥚",
        "summary": "Tuxum qo'yuvchi, og'izda saqlovchi va tirik tug'uvchi baliqlar chavoqlari parvarishi.",
        "content": (
            "🥚 <b>KO'PAYTIRISH VA CHAVOQ PARVARISHI</b>\n\n"
            "Akvariumda baliqlarni ko'paytirish — to'g'ri oziqlantirish, toza suv va barqaror jinsiy nisbat (odatda 1 erkak va 3-4 urg'ochi) natijasidir.\n\n"
            "🐣 <b>Ko'payish turlari bo'yicha parvarish:</b>\n"
            "• <b>Og'izda saqlovchilar (Mouthbrooders — Malavi, Tanganika):</b>\n"
            "Urg'ochi tuxumni 21–25 kun og'zida saqlaydi va bu vaqtda ovqat yemaydi. Urg'ochini tinch alohida idishga ajratish lozim. Chiqqan chavoqlar katta bo'ladi va darhol ovqat yeya oladi.\n\n"
            "• <b>Substratga tuxum qo'yuvchilar (Cichlidlar, Skalyariya):</b>\n"
            "Tosh yoki yassi barglarga tuxum qo'yadi. Ota-ona tuxumni yelpig'ich qilib kislorod beradi.\n\n"
            "• <b>Tirik tug'uvchilar (Guppi, Molineziya):</b>\n"
            "Chavoqlarni darhol qalin o'simliklar (mox) bilan himoyalash yoki ajratish kerak, aks holda kattalar ularni yeb qo'yadi.\n\n"
            "🥣 <b>Chavoqlar ozuqasi:</b> Yangi chiqqan artemiya naupliyalari (Artemia salina), mikrogijja (Microworm) va maydalangan spirulina."
        ),
    },
    {
        "id": 12,
        "title": "12. Akvariumdagi keng tarqalgan xatolar",
        "category": "Parvarish",
        "emoji": "⚠️",
        "summary": "Yangi boshlovchilar yo'l qo'yadigan 8 ta eng xavfli xato va ulardan saqlanish.",
        "content": (
            "⚠️ <b>AKVARIUMDAGI KENG TARQALGAN 8 TA XATO</b>\n\n"
            "Ushbu ro'yxatni bilish sizni yuzlab muammolardan va nobudgarchiliklardan qutqaradi:\n\n"
            "1. <b>Kichik akvarium oson deb o'ylash:</b> 10 litrli idishda parametrlar tez buziladi. Boshlovchi uchun 60–100 litr ancha barqaror va xavfsiz.\n"
            "2. <b>Haddan tashqari ko'p baliq solish (Overstocking):</b> Hajmiga mos kelmaydigan populyatsiya tezda zaharlanadi.\n"
            "3. <b>Mos kelmaydigan turlarni aralashtirish:</b> Agressiv yirtqich cichlid bilan mayda neontetrani bitta akvariumga qo'yish fojia bilan tugaydi.\n"
            "4. <b>Yorug'likni 12-14 soat yoqib qo'yish:</b> Natijada barcha tosh va oynalarni yashil-jigarrang suvo'tlar (Algae) bosadi. Optimal yorug'lik: kuniga 7–8 soat.\n"
            "5. <b>Filtrni tunda o'chirib qo'yish:</b> Filtrdagi foydali bakteriyalar kislorod yetishmasligidan 3-4 soatda o'ladi. Filtr 24/7 ishlashi shart!\n"
            "6. <b>Filtrni qaynoq yoki jo'mrak suvida yuvish.</b>\n"
            "7. <b>Ortiqcha ovqat berish.</b>\n"
            "8. <b>Suvni to'liq 100% almashtirish.</b>"
        ),
    },
    {
        "id": 13,
        "title": "13. Elektr uzilishi va favqulodda vaziyatlar",
        "category": "Favqulodda",
        "emoji": "⚡",
        "summary": "Chiroq o'chganda kislorodni saqlash, bakteriyalarni qutqarish va harorat himoyasi.",
        "content": (
            "⚡ <b>ELEKTR UZILISHI VA FAVQULODDA VAZIYATLAR</b>\n\n"
            "Elektr energiyasi to'satdan o'chganda nima qilish kerak?\n\n"
            "1. <b>Birinchi xavf — Kislorod tanqisligi (1–3 soat):</b>\n"
            "• Agar zich akvarium bo'lsa, batareya yoki akkumulyatorda ishlovchi ko'chma kompressor zaxirada bo'lishi shart.\n"
            "• Bunday uskuna bo'lmasa, har 30-40 daqiqada akvariumdan krujka bilan suv olib, balanddan qayta quyib kislorod bilan boyitish mumkin.\n\n"
            "2. <b>Ikkinchi xavf — Tashqi filtrdagi bakteriyalar (3–5 soat):</b>\n"
            "• Kanistr filtrda suv oqimi to'xtasa, kislorodsizlikdan foydali bakteriyalar nobud bo'lib, zaharli vodorod sulfid (H2S) ajrata boshlaydi.\n"
            "• Agar elektr 3 soatdan ko'p o'chsa, filtrni to'g'ridan-to'g'ri akvariumga qayta ulamang! Uni oldin chelakda biroz yuvib, iflos suvini to'kib tashlab keyin ishga tushiring.\n\n"
            "3. <b>Uchinchi xavf — Sovuq (qishda):</b>\n"
            "• Akvariumni qalin adyol yoki penoplast bilan o'rab qo'ying, bu issiqlikni ancha vaqt ushlab turadi."
        ),
    },
    {
        "id": 14,
        "title": "14. Baliqlar mosligi va populyatsiya zichligi",
        "category": "Moslik",
        "emoji": "👥",
        "summary": "Baliqlarni to'g'ri birga joylashtirish, hududiy agressiyani boshqarish.",
        "content": (
            "👥 <b>BALIQLAR MOSLIGI VA POPULYATSIYA ZICHLIGI</b>\n\n"
            "Baliqlarni birga saqlashda quyidagi 4 omil to'liq mos kelishi shart:\n\n"
            "1. <b>Suv parametrlari muvofiqligi:</b>\n"
            "Yumshoq kislotali suv baliqlari (Diskus, Neontetra, Apistogramma) hech qachon qattiq ishqoriy ko'l cichlidlari (Malavi, Tanganika) bilan birga yashay olmaydi.\n\n"
            "2. <b>Temperament va tajovuzkorlik:</b>\n"
            "Tinch va sekin suzuvchi baliqlar (Skalyariya, Gurami) tez va o'tkir tishli barbuslar yoki cichlidlar bilan saqlansa, ularning suzgichlari yeb qo'yiladi.\n\n"
            "3. <b>Akvarium qatlamlari:</b>\n"
            "Akvarium barcha qatlamlari bo'ylab teng taqsimlanishi kerak:\n"
            "• Yuqori qatlam: Danio, Xiphophorus\n"
            "• O'rta qatlam: Tetralar, Skalyariya, Rainbowfish\n"
            "• Tub qatlam: Corydoras, Ancistrus, Pleco, Loaches\n\n"
            "4. <b>Boshpanalar:</b> Cichlidlar uchun akvarium uzunligi bo'ylab ko'plab tosh g'orlar qilinishi hudud talashishdagi qirg'inbarotni 80% ga kamaytiradi."
        ),
    },
]
