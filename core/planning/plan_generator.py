import anthropic
import streamlit as st
import json

def generate_plan(profile, health, lifestyle, nutrition, performance, scores, flags):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    flag_list = "\n".join([f"- [{f.priority}] {f.message}" for f in flags]) if flags else "Risk tespit edilmedi."

    prompt = f"""
Sen deneyimli bir sağlık koçusun. Fizyoterapist, diyetisyen ve fitness koçu perspektifini birleştiriyorsun.
Türkçe yanıt ver. Teşhis koyma, doktor yerine geçme.
Sadece JSON döndür, başka hiçbir şey yazma. Markdown veya açıklama ekleme.

## KULLANICI PROFİLİ
Yaş: {profile.get('age')} | Cinsiyet: {profile.get('gender')} | Boy: {profile.get('height_cm')} cm | Kilo: {profile.get('weight_kg')} kg
Aktivite: {profile.get('activity_level')} | Hedef: {performance.get('goal') if performance else 'Belirtilmemiş'}
Beslenme Tipi: {nutrition.get('diet_type') if nutrition else 'Belirtilmemiş'}
Bütçe: {nutrition.get('budget_level') if nutrition else 'Orta'}

## WELLNESS SKORLARI
Metabolik: {scores['metabolic']}/100 | Kardiyovasküler: {scores['cardio']}/100
Beslenme: {scores['nutrition']}/100 | Performans: {scores['performance']}/100
Zihinsel: {scores['mental']}/100 | Genel: {scores['overall']}/100

## RİSKLER
{flag_list}

## BESLENME VERİSİ
Su: {nutrition.get('water_liters') if nutrition else '?'} litre/gün
Sebze/Meyve: {nutrition.get('vegetable_portions') if nutrition else '?'} porsiyon/gün
Balık: {nutrition.get('fish_per_week') if nutrition else '?'}x/hafta
İşlenmiş gıda: {nutrition.get('processed_food_freq') if nutrition else '?'}
Sevmediği yiyecekler: {nutrition.get('disliked_foods') if nutrition else 'Yok'}

## ANTRENMAN VERİSİ
Deneyim: {performance.get('training_experience_mo') if performance else 0} ay
Haftalık gün: {performance.get('training_days_per_week') if performance else 0}
Yer: {performance.get('training_location') if performance else 'Belirtilmemiş'}
Sevmediği egzersizler: {performance.get('disliked_exercises') if performance else 'Yok'}

Aşağıdaki JSON formatında kişiye özel plan üret:

{{
  "beslenme_plani": {{
    "gunluk_kalori": 2000,
    "makrolar": {{
      "protein_g": 150,
      "karbonhidrat_g": 200,
      "yag_g": 70
    }},
    "ogutler": {{
      "sabah": {{
        "saat": "07:30",
        "icerik": "Örnek kahvaltı içeriği",
        "kalori": 450,
        "ipucu": "Neden bu öğün"
      }},
      "ara_ogut_1": {{
        "saat": "10:30",
        "icerik": "Ara öğün içeriği",
        "kalori": 200,
        "ipucu": "Kısa not"
      }},
      "ogle": {{
        "saat": "13:00",
        "icerik": "Öğle yemeği içeriği",
        "kalori": 550,
        "ipucu": "Neden bu öğün"
      }},
      "ara_ogut_2": {{
        "saat": "16:00",
        "icerik": "Ara öğün içeriği",
        "kalori": 200,
        "ipucu": "Kısa not"
      }},
      "aksam": {{
        "saat": "19:30",
        "icerik": "Akşam yemeği içeriği",
        "kalori": 500,
        "ipucu": "Neden bu öğün"
      }}
    }},
    "onerilen_gidalar": ["gıda1", "gıda2", "gıda3", "gıda4", "gıda5"],
    "kacinilacak_gidalar": ["gıda1", "gıda2", "gıda3"],
    "haftalik_ipuclari": ["ipucu1", "ipucu2", "ipucu3"]
  }},
  "antrenman_plani": {{
    "haftalik_yapi": "Örnek: Haftada 3 gün full body",
    "gunler": [
      {{
        "gun": "Pazartesi",
        "tur": "Güç / Kardiyo / Mobilite",
        "sure_dk": 45,
        "egzersizler": [
          {{
            "ad": "Egzersiz adı",
            "set": 3,
            "tekrar": "10-12",
            "dinlenme_sn": 60,
            "not": "Teknik notu"
          }}
        ],
        "isinma": "Isınma açıklaması",
        "soguma": "Soğuma açıklaması"
      }}
    ],
    "haftalik_ipuclari": ["ipucu1", "ipucu2"],
    "ilerleme_protokolu": "Nasıl ilerleyeceği"
  }},
  "supplement_plani": [
    {{
      "ad": "Takviye adı",
      "doz": "Doz miktarı",
      "zamanlama": "Ne zaman alınacak",
      "neden": "Neden öneriliyor",
      "oncelik": 1
    }}
  ],
  "yasam_tarzi_onerileri": [
    {{
      "kategori": "Uyku / Stres / Hareket",
      "oneri": "Öneri açıklaması",
      "nasil": "Nasıl uygulanacak"
    }}
  ],
  "coach_notu": "Kişiye özel, samimi ve motive edici koç notu. 2-3 cümle."
}}
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return {"success": True, "plan": json.loads(raw.strip())}

    except Exception as e:
        return {"success": False, "error": str(e)}