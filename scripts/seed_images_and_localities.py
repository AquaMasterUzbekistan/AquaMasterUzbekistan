"""Seed images and localities for all species in the atlas."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session
from app.models.species import Species, species_localities
from app.models.locality import Lake, Country, Locality
from app.models.image import SpeciesImage, ImageType, VerificationStatus

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("seed_extra")

SPECIES_DATA = [
    {
        "scientific_name": "Pseudotropheus demasoni",
        "locality": {
            "name": "Pombo Rocks",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Tanzaniya",
            "latitude": -10.420,
            "longitude": 34.280,
            "habitat": "Tik qoyali biotope, to'lqinlar uriladigan zona, 3-10 metr chuqurlik. Qoyalar qalin Aufwuchs (suv o'tlari gilami) bilan qoplangan.",
            "description": "Malavi ko'lining Pombo Rocks riflari — Demasoni cichlidasining yagona tabiiy vatani hisoblanadi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Pseudotropheus_demasoni.jpg/800px-Pseudotropheus_demasoni.jpg",
        "caption": "Pseudotropheus demasoni — Pombo Rocks, Lake Malawi",
    },
    {
        "scientific_name": "Labidochromis caeruleus",
        "locality": {
            "name": "Lion's Cove",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -11.517,
            "longitude": 34.317,
            "habitat": "Chuqur qoyali g'orlar va tirqishlar, 10-25 metr chuqurlik. Qorong'i burchaklar va tosh oraliqlari.",
            "description": "Lion's Cove — elektr sariq (Electric Yellow) morfi ilk bor kashf etilgan afsonaviy qo'ltiq."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Labidochromis_caeruleus_%28male%29.jpg/800px-Labidochromis_caeruleus_%28male%29.jpg",
        "caption": "Labidochromis caeruleus — Lion's Cove, Lake Malawi",
    },
    {
        "scientific_name": "Metriaclima lombardoi",
        "locality": {
            "name": "Mbenji Island",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -13.433,
            "longitude": 34.500,
            "habitat": "Orol atrofidagi qoyali va qumli oraliq hudud (intermediate zone), 5-15 metr.",
            "description": "Mbenji oroli — Lombardoi cichlidalarining tabiiy yashash biotopi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Maylandia_lombardoi.jpg/800px-Maylandia_lombardoi.jpg",
        "caption": "Metriaclima lombardoi — Mbenji Island, Lake Malawi",
    },
    {
        "scientific_name": "Chindongo saulosi",
        "locality": {
            "name": "Taiwan Reef",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -11.950,
            "longitude": 34.583,
            "habitat": "Kuchli suv oqimli ochiq ko'l rifi, yuqori qatlam (5-15 m chuqurlik). Qoyalar toza suv bilan yuvilib turadi.",
            "description": "Taiwan Reef — Chindongo saulosi turining dunyodagi yagona tabiiy uyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Pseudotropheus_saulosi.jpg/800px-Pseudotropheus_saulosi.jpg",
        "caption": "Chindongo saulosi — Taiwan Reef, Lake Malawi",
    },
    {
        "scientific_name": "Aulonocara baenschi",
        "locality": {
            "name": "Nkhomo Reef",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -12.983,
            "longitude": 34.300,
            "habitat": "Qoya va qum chegarasidagi oraliq zona, 12-25 metr chuqurlik. Qum ostidagi umurtqasizlarni qidiradi.",
            "description": "Nkhomo Reef (Benga) — sariq tovus (Benga Peacock) cichlidasining kelib chiqish joyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Aulonocara_baenschi.jpg/800px-Aulonocara_baenschi.jpg",
        "caption": "Aulonocara baenschi — Nkhomo Reef, Benga, Lake Malawi",
    },
    {
        "scientific_name": "Sciaenochromis fryeri",
        "locality": {
            "name": "Likoma Island",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -12.067,
            "longitude": 34.733,
            "habitat": "Katta toshlar orasidagi ochiq suv usti zonasi. Mbuna chavoqlarini ovlovchi chaqqon yirtqich.",
            "description": "Likoma oroli — moviy Ali (Electric Blue) ning eng mashhur va yorqin rangli populyatsiyasi joylashgan hudud."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Sciaenochromis_fryeri_male.jpg/800px-Sciaenochromis_fryeri_male.jpg",
        "caption": "Sciaenochromis fryeri — Likoma Island, Lake Malawi",
    },
    {
        "scientific_name": "Cyrtocara moorii",
        "locality": {
            "name": "Maleri Islands",
            "lake": "Malavi ko'li (Nyasa)",
            "country": "Malavi",
            "latitude": -13.900,
            "longitude": 34.617,
            "habitat": "Keng sayoz qumli sohillar, 3-15 metr. Qum tituvchi boshqa yirik baliqlar ortidan ergashadi.",
            "description": "Maleri orollari — Ko'k Delfin cichlidasining qumli biotoplaridan biri."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Cyrtocara_moorii.jpg/800px-Cyrtocara_moorii.jpg",
        "caption": "Cyrtocara moorii — Maleri Islands, Lake Malawi",
    },
    {
        "scientific_name": "Neolamprologus multifasciatus",
        "locality": {
            "name": "Mbita Island",
            "lake": "Tanganika ko'li",
            "country": "Zambiya",
            "latitude": -8.767,
            "longitude": 31.117,
            "habitat": "Neothauma chig'anoqlari konlari bilan qoplangan qumli tub, 10-25 metr chuqurlik.",
            "description": "Mbita Island (Mpulungu) — chig'anoq cichlidalarining ulkan koloniyalari yashovchi mashhur orol."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Neolamprologus_multifasciatus_01.jpg/800px-Neolamprologus_multifasciatus_01.jpg",
        "caption": "Neolamprologus multifasciatus — Mbita Island, Lake Tanganyika",
    },
    {
        "scientific_name": "Cyphotilapia frontosa",
        "locality": {
            "name": "Kigoma",
            "lake": "Tanganika ko'li",
            "country": "Tanzaniya",
            "latitude": -4.877,
            "longitude": 29.627,
            "habitat": "Chuqur qoyali qiyaliklar va g'orlar, 20-50+ metr chuqurlik. Qorong'ilik, sovuq va yuqori bosimli qatlam.",
            "description": "Kigoma — 7 polosali klassik Frontosa cichlidasining asl ilmiy vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Cyphotilapia_frontosa_-_Tanganjika-Beulenkopf.jpg/800px-Cyphotilapia_frontosa_-_Tanganjika-Beulenkopf.jpg",
        "caption": "Cyphotilapia frontosa — Kigoma, Lake Tanganyika (7-stripe)",
    },
    {
        "scientific_name": "Tropheus moorii",
        "locality": {
            "name": "Kasanga",
            "lake": "Tanganika ko'li",
            "country": "Tanzaniya",
            "latitude": -8.717,
            "longitude": 31.133,
            "habitat": "Sayoz quyosh nuri tushadigan qoyali sohillar (0.5-5 metr). Qoyalar ustidagi yashil suv o'tlari bilan oziqlanadi.",
            "description": "Kasanga (Red Rainbow) — eng chiroyli kamalak tusli Tropheus morflaridan biri."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Tropheus_moorii_%27Ilangi%27.jpg/800px-Tropheus_moorii_%27Ilangi%27.jpg",
        "caption": "Tropheus moorii — Kasanga, Lake Tanganyika",
    },
    {
        "scientific_name": "Julidochromis transcriptus",
        "locality": {
            "name": "Gombe",
            "lake": "Tanganika ko'li",
            "country": "Tanzaniya",
            "latitude": -4.667,
            "longitude": 29.633,
            "habitat": "Tik qoyali devorlar va tor tosh yoriqlari. Baliq qoyaga qornini qaratib erkin suzadi.",
            "description": "Gombe milliy bog'i sohillari — nafis Julidochromis transcriptus populyatsiyasi uyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Julidochromis_transcriptus_1.jpg/800px-Julidochromis_transcriptus_1.jpg",
        "caption": "Julidochromis transcriptus — Gombe, Lake Tanganyika",
    },
    {
        "scientific_name": "Altolamprologus calvus",
        "locality": {
            "name": "Chaitika",
            "lake": "Tanganika ko'li",
            "country": "Zambiya",
            "latitude": -8.583,
            "longitude": 30.850,
            "habitat": "Chuqur vertikal qoya tirqishlari, 15-35 metr. Yassi tanasi orqali eng ingichka tosh oralariga kirib ov qiladi.",
            "description": "Chaitika — qora va oq marvarid dog'li Calvus cichlidasining yashash joyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Altolamprologus_calvus_black.jpg/800px-Altolamprologus_calvus_black.jpg",
        "caption": "Altolamprologus calvus — Chaitika, Lake Tanganyika",
    },
    {
        "scientific_name": "Pterophyllum scalare",
        "locality": {
            "name": "Rio Ucayali",
            "lake": "Amazonka havzasi",
            "country": "Peru",
            "latitude": -4.450,
            "longitude": -73.400,
            "habitat": "Sekin oquvchi daryo sohillari, suv bosgan o'rmonlar (Igapó) va suv osti daraxt ildizlari.",
            "description": "Rio Ucayali — yovvoyi Skalyariyaning tabiiy tropik biotopi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Pterophyllum_scalare_Natural_History_Museum_University_of_Pisa.jpg/800px-Pterophyllum_scalare_Natural_History_Museum_University_of_Pisa.jpg",
        "caption": "Pterophyllum scalare — Rio Ucayali, Amazon Basin",
    },
    {
        "scientific_name": "Mikrogeophagus ramirezi",
        "locality": {
            "name": "Llanos del Orinoco",
            "lake": "Orinoko havzasi",
            "country": "Venesuela",
            "latitude": 7.800,
            "longitude": -67.450,
            "habitat": "Iliq, sokin va o'simliklarga boy sayoz suv havzalari, qumli va loyli tub.",
            "description": "Llanos tekisliklari — kapalak cichlidasi (Ramirezi) ning tabiiy vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Mikrogeophagus_ramirezi_male.jpg/800px-Mikrogeophagus_ramirezi_male.jpg",
        "caption": "Mikrogeophagus ramirezi — Llanos, Orinoco River Basin",
    },
    {
        "scientific_name": "Astronotus ocellatus",
        "locality": {
            "name": "Rio Negro / Manaus",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -3.119,
            "longitude": -60.021,
            "habitat": "Sokin daryo qo'ltiqlari, quyuq suv osti ildizlari va qulagan daraxt tanalari osti.",
            "description": "Manaus atrofidagi Amazonka oqimlari — bahaybat va aqlli Oskar (Astronotus) uyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Astronotus_ocellatus.jpg/800px-Astronotus_ocellatus.jpg",
        "caption": "Astronotus ocellatus — Rio Negro / Amazon River",
    },
    {
        "scientific_name": "Thorichthys meeki",
        "locality": {
            "name": "Rio Usumacinta",
            "lake": "Amazonka havzasi",
            "country": "Meksika",
            "latitude": 17.500,
            "longitude": -91.500,
            "habitat": "Ohaktoshli sokin daryo irmoqlari, toshli va qumli sayozliklar.",
            "description": "Usumacinta daryosi havzasi — olov tomoq (Firemouth) cichlidasining kelib chiqish joyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Thorichthys_meeki_01.jpg/800px-Thorichthys_meeki_01.jpg",
        "caption": "Thorichthys meeki — Rio Usumacinta, Mexico",
    },
    {
        "scientific_name": "Amatitlania nigrofasciata",
        "locality": {
            "name": "Lake Amatitlán",
            "lake": "Amazonka havzasi",
            "country": "Gvatemala",
            "latitude": 14.450,
            "longitude": -90.550,
            "habitat": "Toshli va loyli qirg'oqlar, kuchli oqimga chidamli tosh tirqishlari.",
            "description": "Amatitlan ko'li — qora chiziqli mahbus (Convict Cichlid) cichlidasi vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Amatitlania_nigrofasciata_01.jpg/800px-Amatitlania_nigrofasciata_01.jpg",
        "caption": "Amatitlania nigrofasciata — Lake Amatitlán, Central America",
    },
    {
        "scientific_name": "Symphysodon discus",
        "locality": {
            "name": "Rio Negro (Barcelos)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -0.974,
            "longitude": -62.926,
            "habitat": "O'ta kislotali (pH 4.5-5.5) va o'ta yumshoq qora suv (blackwater), suv bosgan botqoq o'rmonlari.",
            "description": "Barcelos shahri atrofi — mashhur Heckel Diskusining dunyodagi yagona tabiiy vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Symphysodon_discus_Heckel.jpg/800px-Symphysodon_discus_Heckel.jpg",
        "caption": "Symphysodon discus (Heckel) — Rio Negro, Barcelos, Brazil",
    },
    {
        "scientific_name": "Symphysodon aequifasciatus",
        "locality": {
            "name": "Rio Solimões (Tefé)",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -3.354,
            "longitude": -64.711,
            "habitat": "Iliq, sokin daryo o'zanlari, loy va ildizlar bilan himoyalangan suv osti pana joylari.",
            "description": "Tefé ko'li va Solimões daryosi — yashil va ko'k diskuslarning tabiiy markazi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%BE%D0%BE%D0%BF%D0%B0%D1%80%D0%BA._%D0%90%D0%BA%D0%B2%D0%B0%D1%80%D0%B8%D1%83%D0%BC.8_-_panoramio.jpg/800px-%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0%B5%D0%B2%D1%81%D0%BA%D0%B8%D0%B9_%D0%B7%D0%BE%D0%BE%D0%BF%D0%B0%D1%80%D0%BA._%D0%90%D0%BA%D0%B2%D0%B0%D1%80%D0%B8%D1%83%D0%BC.8_-_panoramio.jpg",
        "caption": "Symphysodon aequifasciatus — Lake Tefé, Rio Solimões",
    },
    {
        "scientific_name": "Paracheirodon innesi",
        "locality": {
            "name": "Rio Putumayo",
            "lake": "Amazonka havzasi",
            "country": "Peru",
            "latitude": -2.500,
            "longitude": -72.000,
            "habitat": "Soyabonli zich tropik o'rmon ostidagi salqin, qorong'i va yumshoq o'rmon irmoqlari.",
            "description": "Putumayo daryosi havzasi — oddiy Neon balig'ining tabiiy vatanidir."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Neonsalmler_Paracheirodon_innesi.jpg/800px-Neonsalmler_Paracheirodon_innesi.jpg",
        "caption": "Paracheirodon innesi — Rio Putumayo, Peru",
    },
    {
        "scientific_name": "Betta splendens",
        "locality": {
            "name": "Chao Phraya Floodplains",
            "lake": "Chao Phraya daryosi",
            "country": "Tailand",
            "latitude": 13.750,
            "longitude": 100.516,
            "habitat": "Iliq, sayoz sholizorlar, botqoqliklar va tinch oquvchi kanallar. Qalin suzuvchi o'simliklar.",
            "description": "Markaziy Tailand sholizorlari va botqoqlari — Siom jangovar balig'i (Betta) ning asl vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Betta_splendens_male_red.jpg/800px-Betta_splendens_male_red.jpg",
        "caption": "Betta splendens — Central Thailand Wetlands",
    },
    {
        "scientific_name": "Puntigrus tetrazona",
        "locality": {
            "name": "Sumatra Peat Swamps",
            "lake": "Chao Phraya daryosi",
            "country": "Indoneziya",
            "latitude": -0.500,
            "longitude": 101.500,
            "habitat": "Torfli botqoq o'rmon irmoqlari, toza va yumshoq suv, qumli va bargli tub.",
            "description": "Sumatra va Kalimantan orollari — Sumatra barbusi uyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Puntius_tetrazona_1.jpg/800px-Puntius_tetrazona_1.jpg",
        "caption": "Puntigrus tetrazona — Sumatra, Indonesia",
    },
    {
        "scientific_name": "Poecilia reticulata",
        "locality": {
            "name": "Trinidad Mountain Streams",
            "lake": "Orinoko havzasi",
            "country": "Venesuela",
            "latitude": 10.500,
            "longitude": -61.300,
            "habitat": "Tog'dan oqib tushuvchi toza, kislorodga boy sayoz soylar va ko'lmaklar.",
            "description": "Trinidad oroli va shimoliy Venesuela — yovvoyi Guppi balig'ining ilmiy vatanidir."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Guppy_Poecilia_reticulata.jpg/800px-Guppy_Poecilia_reticulata.jpg",
        "caption": "Poecilia reticulata — Trinidad Streams",
    },
    {
        "scientific_name": "Corydoras paleatus",
        "locality": {
            "name": "Rio de la Plata Basin",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -34.500,
            "longitude": -58.500,
            "habitat": "Qumli va loyli sayoz daryo bo'ylari, salqinroq subtropik suv.",
            "description": "La Plata havzasi — marmar koridoras (Punctated Corydoras) ning vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Corydoras_paleatus_1.jpg/800px-Corydoras_paleatus_1.jpg",
        "caption": "Corydoras paleatus — La Plata River Basin",
    },
    {
        "scientific_name": "Ancistrus cirrhosus",
        "locality": {
            "name": "Rio Paraná",
            "lake": "Amazonka havzasi",
            "country": "Braziliya",
            "latitude": -27.000,
            "longitude": -56.000,
            "habitat": "Tez oquvchi toshli va daraxt tanalariga boy daryo tublari. Qoyalardagi suv o'tlarini qiradi.",
            "description": "Parana daryosi — yopishqoq mo'ylovli som (Ancistrus) ning tabiiy biotopi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Ancistrus_cirrhosus_1.jpg/800px-Ancistrus_cirrhosus_1.jpg",
        "caption": "Ancistrus cirrhosus — Rio Paraná Basin",
    },
    {
        "scientific_name": "Chromobotia macracanthus",
        "locality": {
            "name": "Batang Hari River",
            "lake": "Chao Phraya daryosi",
            "country": "Indoneziya",
            "latitude": -1.500,
            "longitude": 103.500,
            "habitat": "Tez va toza oquvchi yirik daryo o'zanlari, tosh va mayda shag'alli tub.",
            "description": "Sumatra orolidagi Batang Hari daryosi — mashhur Klobuk (Clown Loach) balig'ining vatani."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Chromobotia_macracanthus_1.jpg/800px-Chromobotia_macracanthus_1.jpg",
        "caption": "Chromobotia macracanthus — Batang Hari River, Sumatra",
    },
    {
        "scientific_name": "Neocaridina davidi",
        "locality": {
            "name": "Taiwan Mountain Streams",
            "lake": "Chao Phraya daryosi",
            "country": "Tailand",
            "latitude": 24.500,
            "longitude": 121.000,
            "habitat": "O'simliklar va yaproqlarga boy sokin tog' soylari, toza va salqin suv.",
            "description": "Tayvan va Sharqiy Osiyo soylari — gilos krevetkasi (Red Cherry) ning asl tabiiy uyi."
        },
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Red_cherry_shrimp.jpg/800px-Red_cherry_shrimp.jpg",
        "caption": "Neocaridina davidi (Red Cherry) — Taiwan Mountain Streams",
    },
]


async def seed_localities_and_images():
    """Populate locality atlas and verified images for all species."""
    logger.info("Connecting to database...")
    async with async_session() as session:
        # Load lakes and countries map
        res_lakes = await session.execute(select(Lake))
        lakes_map = {lake.name: lake.id for lake in res_lakes.scalars().all()}

        res_countries = await session.execute(select(Country))
        countries_map = {c.name: c.id for c in res_countries.scalars().all()}

        # Load all species
        res_species = await session.execute(select(Species))
        species_map = {sp.scientific_name: sp for sp in res_species.scalars().all()}

        for item in SPECIES_DATA:
            sc_name = item["scientific_name"]
            sp = species_map.get(sc_name)
            if not sp:
                logger.warning(f"Species {sc_name} not found in DB! Skipping.")
                continue

            loc_info = item["locality"]
            lake_id = lakes_map.get(loc_info["lake"])
            country_id = countries_map.get(loc_info["country"])

            # Check or create Locality
            res_loc = await session.execute(
                select(Locality).where(Locality.name == loc_info["name"])
            )
            loc = res_loc.scalar_one_or_none()
            if not loc:
                loc = Locality(
                    name=loc_info["name"],
                    lake_id=lake_id,
                    country_id=country_id,
                    latitude=loc_info["latitude"],
                    longitude=loc_info["longitude"],
                    habitat=loc_info["habitat"],
                    description=loc_info["description"],
                )
                session.add(loc)
                await session.flush()
                logger.info(f"Created Locality: {loc.name}")
            else:
                # Update coordinates and habitat
                loc.lake_id = lake_id
                loc.country_id = country_id
                loc.latitude = loc_info["latitude"]
                loc.longitude = loc_info["longitude"]
                loc.habitat = loc_info["habitat"]
                loc.description = loc_info["description"]
                await session.flush()

            # Link species to locality if not already linked
            link_check = await session.execute(
                select(species_localities).where(
                    species_localities.c.species_id == sp.id,
                    species_localities.c.locality_id == loc.id,
                )
            )
            if not link_check.first():
                await session.execute(
                    species_localities.insert().values(
                        species_id=sp.id,
                        locality_id=loc.id,
                    )
                )
                logger.info(f"Linked {sp.scientific_name} -> {loc.name}")

            # Check or create SpeciesImage
            res_img = await session.execute(
                select(SpeciesImage).where(
                    SpeciesImage.species_id == sp.id,
                    SpeciesImage.image_type == ImageType.MAIN,
                )
            )
            img = res_img.scalar_one_or_none()
            if not img:
                img = SpeciesImage(
                    species_id=sp.id,
                    image_url=item["image_url"],
                    image_type=ImageType.MAIN,
                    caption=item["caption"],
                    source="Wikimedia Commons / Encyclopedia",
                    verification=VerificationStatus.VERIFIED,
                    sort_order=1,
                )
                session.add(img)
                logger.info(f"Created SpeciesImage for {sp.scientific_name}")
            else:
                img.image_url = item["image_url"]
                img.caption = item["caption"]
                img.source = "Wikimedia Commons / Encyclopedia"
                img.verification = VerificationStatus.VERIFIED

        await session.commit()
        logger.info("Successfully seeded all localities and species images!")


if __name__ == "__main__":
    asyncio.run(seed_localities_and_images())
