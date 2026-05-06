import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── FONT KAYIT ────────────────────────────────────────────
_fonts_registered = False

def register_fonts():
    global _fonts_registered
    if _fonts_registered:
        return
    # Proje kök dizinini bul
    base = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),  # core/
        "..",                                          # ai_wellness/
        "assets", "fonts"
    )
    base = os.path.normpath(base)
    
    pdfmetrics.registerFont(TTFont("DejaVu",            os.path.join(base, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold",       os.path.join(base, "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Italic",     os.path.join(base, "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", os.path.join(base, "DejaVuSans-BoldOblique.ttf")))
    from reportlab.lib.fonts import addMapping
    addMapping("DejaVu", 0, 0, "DejaVu")
    addMapping("DejaVu", 1, 0, "DejaVu-Bold")
    addMapping("DejaVu", 0, 1, "DejaVu-Italic")
    addMapping("DejaVu", 1, 1, "DejaVu-BoldItalic")
    _fonts_registered = True


# Renkler
PRIMARY    = HexColor("#1B4F72")
ACCENT     = HexColor("#2E86AB")
LIGHT_BLUE = HexColor("#D6EAF8")
GREEN      = HexColor("#1E8449")
LIGHT_GREEN= HexColor("#D5F5E3")
ORANGE     = HexColor("#CA6F1E")
LIGHT_ORANGE=HexColor("#FDEBD0")
RED        = HexColor("#922B21")
LIGHT_RED  = HexColor("#FADBD8")
GRAY       = HexColor("#5D6D7E")
LIGHT_GRAY = HexColor("#F2F3F4")
WHITE      = white
BLACK      = black

def get_styles(lang="tr"):
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Title1",
        fontSize=24, fontName="DejaVu-Bold",
        textColor=PRIMARY, spaceAfter=6,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name="Title2",
        fontSize=14, fontName="DejaVu-Bold",
        textColor=PRIMARY, spaceBefore=12, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="Title3",
        fontSize=11, fontName="DejaVu-Bold",
        textColor=ACCENT, spaceBefore=8, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=9, fontName="DejaVu",
        textColor=BLACK, spaceAfter=4, leading=14
    ))
    styles.add(ParagraphStyle(
        name="Caption",
        fontSize=8, fontName="DejaVu",
        textColor=GRAY, spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="Center",
        fontSize=9, fontName="DejaVu",
        alignment=TA_CENTER, textColor=BLACK
    ))
    styles.add(ParagraphStyle(
        name="Warning",
        fontSize=8, fontName="DejaVu",
        textColor=ORANGE, spaceAfter=4
    ))
    return styles

def score_color(score):
    if score >= 75: return GREEN
    if score >= 50: return ORANGE
    return RED

def score_label(score, lang):
    if lang == "tr":
        if score >= 75: return "İyi"
        if score >= 50: return "Orta"
        return "Düşük"
    else:
        if score >= 75: return "Good"
        if score >= 50: return "Fair"
        return "Low"

def build_cover(story, styles, user_info, lang):
    story.append(Spacer(1, 2*cm))
    title = "AI WELLNESS" 
    subtitle = "Kişiselleştirilmiş Sağlık & Performans Raporu" if lang == "tr" else "Personalized Health & Performance Report"
    story.append(Paragraph(title, styles["Title1"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(subtitle, styles["Title2"]))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 0.5*cm))

    info_label = "Rapor Bilgileri" if lang == "tr" else "Report Information"
    name_label = "Ad" if lang == "tr" else "Name"
    date_label = "Tarih" if lang == "tr" else "Date"
    note_label = "Not" if lang == "tr" else "Note"
    note_text  = "Bu rapor bilgi amaçlıdır. Tıbbi tavsiye niteliği taşımaz." if lang == "tr" else "This report is for informational purposes only. Not medical advice."

    data = [
        [Paragraph(f"<b>{info_label}</b>", styles["Body"]), ""],
        [Paragraph(f"{name_label}:", styles["Body"]),
         Paragraph(user_info.get("name", "—"), styles["Body"])],
        [Paragraph(f"{date_label}:", styles["Body"]),
         Paragraph(str(date.today()), styles["Body"])],
        [Paragraph(f"{note_label}:", styles["Body"]),
         Paragraph(note_text, styles["Warning"])],
    ]
    t = Table(data, colWidths=[4*cm, 13*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), LIGHT_BLUE),
        ("SPAN",       (0,0), (-1,0)),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",        (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",  (0,0), (-1,-1), 0.25, GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(PageBreak())

def build_scores_section(story, styles, scores, flags, lang):
    title = "WELLNESS ANALİZİ" if lang == "tr" else "WELLNESS ANALYSIS"
    story.append(Paragraph(title, styles["Title2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.3*cm))

    # Genel skor
    overall = scores.get("overall", 0)
    overall_label = "Genel Wellness Skoru" if lang == "tr" else "Overall Wellness Score"
    data = [[
        Paragraph(f"<b>{overall_label}</b>", styles["Title2"]),
        Paragraph(f"<b>{overall}/100</b>", ParagraphStyle(
            "BigScore", fontSize=22, fontName="DejaVu-Bold",
            textColor=score_color(overall), alignment=TA_CENTER
        )),
        Paragraph(f"<b>{score_label(overall, lang)}</b>", ParagraphStyle(
            "ScoreLabel", fontSize=14, fontName="DejaVu-Bold",
            textColor=score_color(overall), alignment=TA_CENTER
        ))
    ]]
    t = Table(data, colWidths=[9*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BLUE),
        ("BOX", (0,0), (-1,-1), 1, PRIMARY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Kategori skorları
    cats_tr = ["Metabolik", "Kardiyovasküler", "Kas-İskelet", "Beslenme", "Zihinsel", "Performans"]
    cats_en = ["Metabolic", "Cardiovascular", "Musculoskeletal", "Nutrition", "Mental", "Performance"]
    cats    = cats_tr if lang == "tr" else cats_en
    keys    = ["metabolic", "cardio", "msk", "nutrition", "mental", "performance"]

    header_score = "Skor" if lang == "tr" else "Score"
    header_status= "Durum" if lang == "tr" else "Status"
    header_cat   = "Kategori" if lang == "tr" else "Category"

    data = [[
        Paragraph(f"<b>{header_cat}</b>", styles["Body"]),
        Paragraph(f"<b>{header_score}</b>", styles["Center"]),
        Paragraph(f"<b>{header_status}</b>", styles["Center"]),
        Paragraph("<b>Bar</b>", styles["Center"])
    ]]

    for cat, key in zip(cats, keys):
        score = scores.get(key, 0)
        bar_width = int(score * 0.8)
        bar = "█" * (bar_width // 5) + "░" * ((80 - bar_width) // 5)
        data.append([
            Paragraph(cat, styles["Body"]),
            Paragraph(f"{score}/100", styles["Center"]),
            Paragraph(score_label(score, lang), ParagraphStyle(
                f"sl_{key}", fontSize=9, fontName="DejaVu-Bold",
                textColor=score_color(score), alignment=TA_CENTER
            )),
            Paragraph(bar[:12], ParagraphStyle(
                f"bar_{key}", fontSize=7, fontName="DejaVu",
                textColor=score_color(score)
            ))
        ])

    t = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",     (0,0), (-1,-1), 0.25, GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Riskler
    if flags:
        risks_title = "Tespit Edilen Riskler" if lang == "tr" else "Identified Risks"
        story.append(Paragraph(risks_title, styles["Title3"]))

        priority_order = {"KRİTİK": 0, "YÜKSEK": 1, "ORTA": 2, "DÜŞÜK": 3}
        sorted_flags = sorted(flags, key=lambda f: priority_order.get(f.priority, 4))

        p_colors = {"KRİTİK": RED, "YÜKSEK": ORANGE, "ORTA": HexColor("#B7950B"), "DÜŞÜK": ACCENT}
        p_bg     = {"KRİTİK": LIGHT_RED, "YÜKSEK": LIGHT_ORANGE, "ORTA": HexColor("#FEF9E7"), "DÜŞÜK": LIGHT_BLUE}

        for f in sorted_flags[:8]:
            color = p_colors.get(f.priority, GRAY)
            bg    = p_bg.get(f.priority, LIGHT_GRAY)
            action_label = "Öneri" if lang == "tr" else "Action"
            data = [[
                Paragraph(f"<b>[{f.priority}]</b> {f.message}", ParagraphStyle(
                    f"flag_{f.code}", fontSize=9, fontName="DejaVu",
                    textColor=color
                )),
                Paragraph(f"<b>{action_label}:</b> {f.action}", styles["Caption"])
            ]]
            t = Table(data, colWidths=[8.5*cm, 8.5*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), bg),
                ("BOX",        (0,0), (-1,-1), 0.5, color),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                ("LEFTPADDING",   (0,0), (-1,-1), 8),
                ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.15*cm))

    story.append(PageBreak())

def build_nutrition_section(story, styles, plan_data, lang):
    title = "BESLENME PLANI" if lang == "tr" else "NUTRITION PLAN"
    story.append(Paragraph(title, styles["Title2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.3*cm))

    bp = plan_data.get("beslenme_plani", {})
    if not bp:
        no_data = "Beslenme planı bulunamadı." if lang == "tr" else "No nutrition plan found."
        story.append(Paragraph(no_data, styles["Body"]))
        return

    # Makrolar
    makro = bp.get("makrolar", {})
    kalori = bp.get("gunluk_kalori", 0)
    cal_label    = "Günlük Kalori" if lang == "tr" else "Daily Calories"
    protein_label= "Protein" if lang == "tr" else "Protein"
    carb_label   = "Karbonhidrat" if lang == "tr" else "Carbohydrates"
    fat_label    = "Yağ" if lang == "tr" else "Fat"

    data = [[
        Paragraph(f"<b>{cal_label}</b>\n{kalori} kcal", styles["Center"]),
        Paragraph(f"<b>{protein_label}</b>\n{makro.get('protein_g',0)}g", styles["Center"]),
        Paragraph(f"<b>{carb_label}</b>\n{makro.get('karbonhidrat_g',0)}g", styles["Center"]),
        Paragraph(f"<b>{fat_label}</b>\n{makro.get('yag_g',0)}g", styles["Center"]),
    ]]
    t = Table(data, colWidths=[4.25*cm]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BLUE),
        ("BOX",        (0,0), (-1,-1), 0.5, ACCENT),
        ("INNERGRID",  (0,0), (-1,-1), 0.25, ACCENT),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Öğünler
    ogut_labels_tr = {
        "sabah": "Kahvaltı", "ara_ogut_1": "Ara Öğün 1",
        "ogle": "Öğle", "ara_ogut_2": "Ara Öğün 2", "aksam": "Akşam"
    }
    ogut_labels_en = {
        "sabah": "Breakfast", "ara_ogut_1": "Snack 1",
        "ogle": "Lunch", "ara_ogut_2": "Snack 2", "aksam": "Dinner"
    }
    ogut_labels = ogut_labels_tr if lang == "tr" else ogut_labels_en

    time_h = "Saat" if lang == "tr" else "Time"
    cal_h  = "Kalori" if lang == "tr" else "Calories"
    con_h  = "İçerik" if lang == "tr" else "Content"
    tip_h  = "İpucu" if lang == "tr" else "Tip"

    header = [
        Paragraph(f"<b>Öğün</b>" if lang == "tr" else "<b>Meal</b>", styles["Body"]),
        Paragraph(f"<b>{time_h}</b>", styles["Center"]),
        Paragraph(f"<b>{cal_h}</b>",  styles["Center"]),
        Paragraph(f"<b>{con_h}</b>",  styles["Body"]),
        Paragraph(f"<b>{tip_h}</b>",  styles["Body"]),
    ]
    data = [header]
    ogutler = bp.get("ogutler", {})
    for key, label in ogut_labels.items():
        ogut = ogutler.get(key, {})
        if ogut:
            data.append([
                Paragraph(label, styles["Body"]),
                Paragraph(ogut.get("saat", ""), styles["Center"]),
                Paragraph(f"{ogut.get('kalori',0)} kcal", styles["Center"]),
                Paragraph(ogut.get("icerik", ""), styles["Body"]),
                Paragraph(ogut.get("ipucu", ""), styles["Caption"]),
            ])

    t = Table(data, colWidths=[2.5*cm, 1.8*cm, 2*cm, 7*cm, 3.7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",     (0,0), (-1,-1), 0.25, GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Önerilen & kaçınılacak
    col1_title = "Önerilen Gıdalar" if lang == "tr" else "Recommended Foods"
    col2_title = "Kaçınılacak Gıdalar" if lang == "tr" else "Foods to Avoid"
    rec  = bp.get("onerilen_gidalar", [])
    avoid= bp.get("kacinilacak_gidalar", [])
    if rec or avoid:
        rec_text  = "\n".join([f"• {g}" for g in rec])
        avoid_text= "\n".join([f"• {g}" for g in avoid])
        data = [[
            Paragraph(f"<b>{col1_title}</b>\n{rec_text}",   styles["Body"]),
            Paragraph(f"<b>{col2_title}</b>\n{avoid_text}", styles["Body"]),
        ]]
        t = Table(data, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), LIGHT_GREEN),
            ("BACKGROUND", (1,0), (1,-1), LIGHT_RED),
            ("BOX",        (0,0), (-1,-1), 0.5, GRAY),
            ("INNERGRID",  (0,0), (-1,-1), 0.5, GRAY),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ]))
        story.append(t)

    story.append(PageBreak())

def build_training_section(story, styles, plan_data, lang):
    title = "ANTRENMAN PLANI" if lang == "tr" else "TRAINING PLAN"
    story.append(Paragraph(title, styles["Title2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.3*cm))

    ap = plan_data.get("antrenman_plani", {})
    if not ap:
        no_data = "Antrenman planı bulunamadı." if lang == "tr" else "No training plan found."
        story.append(Paragraph(no_data, styles["Body"]))
        return

    weekly_label = "Haftalık Yapı" if lang == "tr" else "Weekly Structure"
    story.append(Paragraph(f"<b>{weekly_label}:</b> {ap.get('haftalik_yapi', '')}", styles["Body"]))
    story.append(Spacer(1, 0.3*cm))

    day_h  = "Gün" if lang == "tr" else "Day"
    type_h = "Tür" if lang == "tr" else "Type"
    dur_h  = "Süre" if lang == "tr" else "Duration"
    ex_h   = "Egzersiz" if lang == "tr" else "Exercise"
    set_h  = "Set" if lang == "tr" else "Sets"
    rep_h  = "Tekrar" if lang == "tr" else "Reps"
    rest_h = "Dinlenme" if lang == "tr" else "Rest"

    for gun in ap.get("gunler", []):
        story.append(Paragraph(
            f"<b>{gun.get('gun','')} — {gun.get('tur','')} ({gun.get('sure_dk',0)} dk)</b>",
            styles["Title3"]
        ))

        if gun.get("isinma"):
            isinma_label = "Isınma" if lang == "tr" else "Warm-up"
            story.append(Paragraph(f"<b>{isinma_label}:</b> {gun['isinma']}", styles["Caption"]))

        egzersizler = gun.get("egzersizler", [])
        if egzersizler:
            header = [
                Paragraph(f"<b>{ex_h}</b>",  styles["Body"]),
                Paragraph(f"<b>{set_h}</b>",  styles["Center"]),
                Paragraph(f"<b>{rep_h}</b>",  styles["Center"]),
                Paragraph(f"<b>{rest_h}</b>", styles["Center"]),
                Paragraph("<b>Not</b>" if lang == "tr" else "<b>Note</b>", styles["Body"]),
            ]
            data = [header]
            for e in egzersizler:
                data.append([
                    Paragraph(e.get("ad", ""), styles["Body"]),
                    Paragraph(str(e.get("set", 0)), styles["Center"]),
                    Paragraph(str(e.get("tekrar", 0)), styles["Center"]),
                    Paragraph(f"{e.get('dinlenme_sn',60)}sn", styles["Center"]),
                    Paragraph(e.get("not", ""), styles["Caption"]),
                ])
            t = Table(data, colWidths=[5*cm, 1.5*cm, 2*cm, 2.5*cm, 6*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), ACCENT),
                ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
                ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
                ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
                ("INNERGRID",     (0,0), (-1,-1), 0.25, GRAY),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                ("LEFTPADDING",   (0,0), (-1,-1), 6),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(t)

        if gun.get("soguma"):
            soguma_label = "Soğuma" if lang == "tr" else "Cool-down"
            story.append(Paragraph(f"<b>{soguma_label}:</b> {gun['soguma']}", styles["Caption"]))
        story.append(Spacer(1, 0.3*cm))

    if ap.get("ilerleme_protokolu"):
        prog_label = "İlerleme Protokolü" if lang == "tr" else "Progression Protocol"
        story.append(Paragraph(f"<b>{prog_label}:</b> {ap['ilerleme_protokolu']}", styles["Body"]))

    story.append(PageBreak())

def build_supplement_section(story, styles, plan_data, lang):
    title = "SUPPLEMENt PLANI" if lang == "tr" else "SUPPLEMENT PLAN"
    story.append(Paragraph(title, styles["Title2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.3*cm))

    sp = plan_data.get("supplement_plani", [])
    if not sp:
        no_data = "Supplement planı bulunamadı." if lang == "tr" else "No supplement plan found."
        story.append(Paragraph(no_data, styles["Body"]))
        return

    pri_h  = "#" if lang == "tr" else "#"
    name_h = "Takviye" if lang == "tr" else "Supplement"
    dose_h = "Doz" if lang == "tr" else "Dose"
    time_h = "Zamanlama" if lang == "tr" else "Timing"
    why_h  = "Neden" if lang == "tr" else "Why"

    header = [
        Paragraph(f"<b>{pri_h}</b>",   styles["Center"]),
        Paragraph(f"<b>{name_h}</b>",  styles["Body"]),
        Paragraph(f"<b>{dose_h}</b>",  styles["Body"]),
        Paragraph(f"<b>{time_h}</b>",  styles["Body"]),
        Paragraph(f"<b>{why_h}</b>",   styles["Body"]),
    ]
    data = [header]
    sp_sorted = sorted(sp, key=lambda x: x.get("oncelik", 99))
    for i, sup in enumerate(sp_sorted):
        data.append([
            Paragraph(str(i+1), styles["Center"]),
            Paragraph(f"<b>{sup.get('ad','')}</b>", styles["Body"]),
            Paragraph(sup.get("doz", ""),            styles["Body"]),
            Paragraph(sup.get("zamanlama", ""),       styles["Body"]),
            Paragraph(sup.get("neden", ""),           styles["Caption"]),
        ])

    t = Table(data, colWidths=[1*cm, 4*cm, 3*cm, 3.5*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",     (0,0), (-1,-1), 0.25, GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(t)
    story.append(PageBreak())

def build_footer_section(story, styles, plan_data, lang):
    # Yaşam tarzı önerileri
    yasam = plan_data.get("yasam_tarzi_onerileri", [])
    if yasam:
        title = "YAŞAM TARZI ÖNERİLERİ" if lang == "tr" else "LIFESTYLE RECOMMENDATIONS"
        story.append(Paragraph(title, styles["Title2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))
        for oneri in yasam:
            with_label = "Nasıl" if lang == "tr" else "How"
            data = [[
                Paragraph(f"<b>{oneri.get('kategori','')}</b>\n{oneri.get('oneri','')}", styles["Body"]),
                Paragraph(f"<b>{with_label}:</b>\n{oneri.get('nasil','')}", styles["Caption"]),
            ]]
            t = Table(data, colWidths=[9*cm, 8*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), LIGHT_BLUE),
                ("BOX",        (0,0), (-1,-1), 0.5, ACCENT),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (-1,-1), 8),
                ("VALIGN",     (0,0), (-1,-1), "TOP"),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.2*cm))
        story.append(Spacer(1, 0.4*cm))

    # Koç notu
    coach_note = plan_data.get("coach_notu", "")
    if coach_note:
        note_title = "KOÇTAN NOT" if lang == "tr" else "NOTE FROM YOUR COACH"
        story.append(Paragraph(note_title, styles["Title2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f'"{coach_note}"', ParagraphStyle(
            "CoachNote", fontSize=11, fontName="DejaVu-Italic",
            textColor=PRIMARY, leftIndent=20, rightIndent=20,
            spaceAfter=12, leading=18
        )))

    # Yasal uyarı
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    warning = (
        "⚠️ Bu rapor bilgi amaçlıdır. Tıbbi teşhis veya tedavi önerisi niteliği taşımaz. "
        "Herhangi bir sağlık kararı almadan önce doktorunuza danışınız. AI Wellness © 2025"
        if lang == "tr" else
        "⚠️ This report is for informational purposes only. Not intended as medical advice or diagnosis. "
        "Consult your physician before making any health decisions. AI Wellness © 2025"
    )
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(warning, styles["Caption"]))

def generate_pdf(user_info, scores, flags, plan_data, lang="tr") -> bytes:
    register_fonts()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = get_styles(lang)
    story  = []

    build_cover(story, styles, user_info, lang)
    build_scores_section(story, styles, scores, flags, lang)
    build_nutrition_section(story, styles, plan_data, lang)
    build_training_section(story, styles, plan_data, lang)
    build_supplement_section(story, styles, plan_data, lang)
    build_footer_section(story, styles, plan_data, lang)

    doc.build(story)
    return buffer.getvalue()