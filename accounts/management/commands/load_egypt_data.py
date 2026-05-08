from django.core.management.base import BaseCommand
from accounts.models import Governorate, City

EGYPT_DATA = {
    "القاهرة": {"en": "Cairo", "cities": [
        ("مدينة نصر", "Nasr City"), ("مصر الجديدة", "Heliopolis"), ("المعادي", "Maadi"),
        ("الزمالك", "Zamalek"), ("المهندسين", "Mohandessin"), ("الدقي", "Dokki"),
        ("عين شمس", "Ain Shams"), ("شبرا", "Shubra"), ("حلوان", "Helwan"),
        ("التجمع الأول", "First Settlement"), ("التجمع الخامس", "Fifth Settlement"),
        ("15 مايو", "15 May City"), ("المطرية", "El Matareya"), ("السيدة زينب", "El Sayeda Zainab"),
        ("باب الشعرية", "Bab El Shareia"), ("الأزبكية", "Azbakeya"), ("بولاق", "Boulaq"),
        ("الوايلي", "El Waily"), ("مصر القديمة", "Old Cairo"), ("الخليفة", "El Khalifa"),
    ]},
    "الجيزة": {"en": "Giza", "cities": [
        ("الجيزة", "Giza"), ("الشيخ زايد", "Sheikh Zayed"), ("6 اكتوبر", "6th of October"),
        ("الهرم", "Haram"), ("فيصل", "Faisal"), ("امبابة", "Imbaba"),
        ("بولاق الدكرور", "Boulaq Dakrour"), ("العجوزة", "Agouza"), ("الدقي", "Dokki"),
        ("اوسيم", "Osim"), ("كرداسة", "Kerdasa"), ("العياط", "El Ayat"),
        ("البدرشين", "El Badrasheen"), ("الصف", "El Saf"), ("ابو النمرس", "Abu El Nomros"),
    ]},
    "الإسكندرية": {"en": "Alexandria", "cities": [
        ("الاسكندرية", "Alexandria"), ("المنتزه", "Montaza"), ("سيدي جابر", "Sidi Gaber"),
        ("العجمي", "Agami"), ("المعموره", "El Mamoura"), ("برج العرب", "Borg El Arab"),
        ("ابو قير", "Abu Qir"), ("ميامي", "Miami"), ("الجمروك", "Gomrook"),
        ("المنشية", "El Manshia"), ("كليوباترا", "Cleopatra"), ("لوران", "Laurent"),
        ("الشاطبي", "El Shattby"), ("سموحة", "Smoha"), ("العصافرة", "El Asafra"),
    ]},
    "الدقهلية": {"en": "Dakahlia", "cities": [
        ("المنصورة", "Mansoura"), ("طلخا", "Talkha"), ("ميت غمر", "Meet Ghamr"),
        ("دكرنس", "Dekernes"), ("المنزلة", "El Manzala"), ("شربين", "Sherbin"),
        ("السنبلاوين", "El Sinbellaween"), ("الجمالية", "El Gamaliya"), ("بلقاس", "Belqas"),
        ("نبروه", "Nabrouh"), ("اجا", "Aga"), ("بني عبيد", "Beni Ebeid"),
    ]},
    "الشرقية": {"en": "Sharqia", "cities": [
        ("الزقازيق", "Zagazig"), ("العاشر من رمضان", "10th of Ramadan"), ("بلبيس", "Bilbeis"),
        ("منيا القمح", "Minya El Qamh"), ("كفر صقر", "Kafr Saqr"), ("القنايات", "El Qanayat"),
        ("الابراهيمية", "El Ibrahimiya"), ("فاقوس", "Faqous"), ("ابو حماد", "Abu Hammad"),
        ("ههيا", "Hehia"), ("ابو كبير", "Abu Kebir"), ("ديرب نجم", "Deirb Negm"),
    ]},
    "القليوبية": {"en": "Qalyubia", "cities": [
        ("بنها", "Benha"), ("شبرا الخيمة", "Shubra El Khayma"), ("قليوب", "Qalyub"),
        ("العبور", "El Obour"), ("طوخ", "Toukh"), ("قها", "Qaha"),
        ("كفر شكر", "Kafr Shukr"), ("الخانكة", "El Khanka"), ("الخصوص", "El Khossous"),
        ("منشاة القناطر", "Monshat El Qanater"), ("الحوامدية", "El Hawamdeya"),
    ]},
    "الغربية": {"en": "Gharbia", "cities": [
        ("طنطا", "Tanta"), ("المحلة الكبرى", "El Mahalla El Kubra"), ("كفر الزيات", "Kafr El Zayat"),
        ("زفتى", "Zifta"), ("السنطة", "El Santa"), ("قطور", "Qutour"),
        ("بسيون", "Basyoun"), ("سمنود", "Samannoud"),
    ]},
    "المنوفية": {"en": "Menofia", "cities": [
        ("شبين الكوم", "Shibin El Koum"), ("منوف", "Menouf"), ("اشمون", "Ashmoun"),
        ("السادات", "Sadat City"), ("تلا", "Tala"), ("الشهداء", "El Shohada"),
        ("بركة السبع", "Berket El Sab"), ("قويسنا", "Quesna"),
    ]},
    "البحيرة": {"en": "Beheira", "cities": [
        ("دمنهور", "Damanhour"), ("كفر الدوار", "Kafr El Dawwar"), ("رشيد", "Rashid"),
        ("ايتاي البارود", "Itay El Baroud"), ("ابو حمص", "Abu Hummus"), ("المحمودية", "El Mahmoudia"),
        ("حوش عيسى", "Housh Issa"), ("شبراخيت", "Shubrakhit"), ("كوم حمادة", "Koum Hamada"),
        ("الرحمانية", "El Rahmaniya"), ("وادي النطرون", "Wadi El Natrun"),
    ]},
    "كفر الشيخ": {"en": "Kafr El Sheikh", "cities": [
        ("كفر الشيخ", "Kafr El Sheikh"), ("دسوق", "Desouk"), ("فوه", "Fouh"),
        ("مطوبس", "Metoubas"), ("بيلا", "Beila"), ("برج البرلس", "Borg El Borollos"),
        ("الحامول", "El Hamoul"), ("الرياض", "El Reyad"), ("سيدي سالم", "Sidi Salem"),
    ]},
    "دمياط": {"en": "Damietta", "cities": [
        ("دمياط", "Damietta"), ("راس البر", "Ras El Bar"), ("الزرقا", "El Zarqa"),
        ("فارسكور", "Faraskour"), ("كفر سعد", "Kafr Saad"), ("عزبة البرج", "Ezbat El Borg"),
    ]},
    "بورسعيد": {"en": "Port Said", "cities": [
        ("بورسعيد", "Port Said"), ("بورفؤاد", "Port Fuad"),
    ]},
    "الإسماعيلية": {"en": "Ismailia", "cities": [
        ("الاسماعيلية", "Ismailia"), ("ابو صوير", "Abu Suwair"), ("فايد", "Fayed"),
        ("القنطرة شرق", "El Qantara East"), ("القنطرة غرب", "El Qantara West"),
        ("كفر ابو علي", "Kafr Abu Ali"), ("التل الكبير", "El Tal El Kabeer"),
    ]},
    "السويس": {"en": "Suez", "cities": [
        ("السويس", "Suez"), ("عتاقة", "Ataka"), ("الاربعين", "El Arbeen"),
        ("فيصل", "Faisal"), ("الجناين", "El Ganayen"),
    ]},
    "المنيا": {"en": "Minya", "cities": [
        ("المنيا", "Minya"), ("ملوي", "Mallawi"), ("مغاغة", "Maghagha"),
        ("بني مزار", "Beni Mazar"), ("سمالوط", "Samalut"), ("ابو قرقاص", "Abu Qurqas"),
        ("العدوة", "El Adwa"), ("دير مواس", "Deir Mawas"),
    ]},
    "اسيوط": {"en": "Asyut", "cities": [
        ("اسيوط", "Asyut"), ("ديروط", "Dairout"), ("منفلوط", "Manfalut"),
        ("القوصية", "El Qusiya"), ("ابنوب", "Abnub"), ("ابو تيج", "Abu Tig"),
        ("الغنايم", "El Ghanayem"), ("ساحل سليم", "Sahel Selim"), ("البداري", "El Badari"),
    ]},
    "سوهاج": {"en": "Sohag", "cities": [
        ("سوهاج", "Sohag"), ("جرجا", "Gerga"), ("اخميم", "Akhmim"),
        ("طهطا", "Tahta"), ("طما", "Tama"), ("الكوثر", "El Kawthar"),
        ("المراغة", "El Maragha"), ("دار السلام", "Dar El Salam"), ("البلينا", "El Balyana"),
        ("المنشاة", "El Monsha'a"),
    ]},
    "قنا": {"en": "Qena", "cities": [
        ("قنا", "Qena"), ("نجع حمادي", "Nag Hammadi"), ("دشنا", "Dishna"),
        ("قوص", "Qous"), ("ابو طشت", "Abu Tesht"), ("فرشوط", "Farshout"),
        ("نقادة", "Naqada"), ("الوقف", "El Waqf"),
    ]},
    "اسوان": {"en": "Aswan", "cities": [
        ("اسوان", "Aswan"), ("كوم امبو", "Kom Ombo"), ("ادفو", "Edfu"),
        ("نصر النوبة", "Nasr El Nuba"), ("ابو سمبل", "Abu Simbel"),
        ("دراو", "Daraw"), ("كلابشة", "Kalabsha"),
    ]},
    "الاقصر": {"en": "Luxor", "cities": [
        ("الاقصر", "Luxor"), ("اسنا", "Esna"), ("الاقصر الغربية", "Luxor West Bank"),
        ("الزينية", "El Zainiya"), ("ارمنت", "Armant"),
    ]},
    "الفيوم": {"en": "Fayoum", "cities": [
        ("الفيوم", "Fayoum"), ("اطسا", "Itsa"), ("سنورس", "Sinnuris"),
        ("طامية", "Tamia"), ("يوسف الصديق", "Yusuf El Siddiq"),
    ]},
    "بني سويف": {"en": "Beni Suef", "cities": [
        ("بني سويف", "Beni Suef"), ("الفشن", "El Fashn"), ("ببا", "Beba"),
        ("اهناسيا", "Ihnasiya"), ("الواسطي", "El Wasta"), ("سمسطا", "Somasta"),
    ]},
    "البحر الاحمر": {"en": "Red Sea", "cities": [
        ("الغردقة", "Hurghada"), ("سفاجا", "Safaga"), ("القصير", "El Quseir"),
        ("مرسى علم", "Marsa Alam"), ("راس غارب", "Ras Gharib"),
    ]},
    "شمال سيناء": {"en": "North Sinai", "cities": [
        ("العريش", "El Arish"), ("رفح", "Rafah"), ("الشيخ زويد", "Sheikh Zuwaid"),
        ("بير العبد", "Bir El Abd"), ("الحسنة", "El Hassana"),
    ]},
    "جنوب سيناء": {"en": "South Sinai", "cities": [
        ("الطور", "El Tor"), ("شرم الشيخ", "Sharm El Sheikh"), ("دهب", "Dahab"),
        ("نويبع", "Nuweiba"), ("طابا", "Taba"), ("سانت كاترين", "Saint Catherine"),
    ]},
    "مطروح": {"en": "Matrouh", "cities": [
        ("مرسى مطروح", "Mersa Matruh"), ("سيوه", "Siwa"), ("الضبعة", "El Dabaa"),
        ("سيدي براني", "Sidi Barrani"), ("الحمام", "El Hammam"), ("العلمين", "El Alamein"),
    ]},
    "الوادي الجديد": {"en": "New Valley", "cities": [
        ("الخارجة", "El Kharga"), ("الداخلة", "El Dakhla"), ("الفرافرة", "El Farafra"),
        ("بلاط", "Balat"),
    ]},
}


class Command(BaseCommand):
    help = 'Load all Egyptian governorates and cities into the database'

    def handle(self, *args, **kwargs):
        created_gov = 0
        created_city = 0

        for gov_ar, data in EGYPT_DATA.items():
            gov, gov_created = Governorate.objects.get_or_create(
                name_ar=gov_ar,
                defaults={'name_en': data['en'], 'is_active': True}
            )
            if gov_created:
                created_gov += 1
                self.stdout.write(f'  [+] {data["en"]}')

            for city_ar, city_en in data['cities']:
                _, city_created = City.objects.get_or_create(
                    governorate=gov,
                    name_ar=city_ar,
                    defaults={'name_en': city_en, 'shipping_cost': 0, 'is_active': True}
                )
                if city_created:
                    created_city += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done! Added {created_gov} governorates and {created_city} cities.'
        ))
