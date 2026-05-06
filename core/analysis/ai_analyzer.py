import anthropic
import streamlit as st
import json
import os
def build_prompt(profile, health, lifestyle, nutrition, performance, scores, flags) -> str:
    flag_list = "\n".join([f"- [{f.priority}] {f.message} → {f.action}" for f in flags])

    return f"""
Sen deneyimli bir sağlık koçusun. Fizyoterapist, diyetisyen, fitness koçu ve psikolog perspektifini birleştiriyorsun.
Teşhis koyma. Doktor yerine geçme. Kanıta dayalı, uygulanabilir öneriler sun.
Türkçe yanıt ver. Sade ve motive edici bir dil kullan.

## KULLANICI PROFİLİ
Yaş: {profile.get('age')} | Cinsiyet: {profile.get('gender')} | Boy: {profile.get('height_cm')} cm | Kilo: {profile.get('weight_kg')} kg
Aktivite: {profile.get('activity_level')} | Meslek: {profile.get('occupation_type')} | Şehir: {profile.get('city')}

## WELLNESS SKORLARI
- Metabolik:     {scores['metabolic']}/100
- Kardiyovasküler: {scores['cardio']}/100
- Kas-İskelet:   {scores['msk']}/100
- Beslenme:      {scores['nutrition']}/100
- Zihinsel:      {scores['mental']}/100
- Performans:    {scores['performance']}/100
- GENEL:         {scores['overall']}/100

## TESPİT EDİLEN RISKLER
{flag_list if flag_list else "Kritik risk tespit edilmedi."}

## SAĞLIK VERİLERİ
Sabah Enerjisi: {health.get('energy_morning') if health else 'Yok'}/10
Uyku Kalitesi: {health.get('sleep_quality') if health else 'Yok'}/10
Uyku Süresi: {health.get('sleep_duration_hrs') if health else 'Yok'} saat
Odak: {health.get('focus_score') if health else 'Yok'}/10
Ruh Hali: {health.get('mood_score') if health else 'Yok'}/10
Sindirim: {health.get('digestion_score') if health else 'Yok'}/10

## BESLENME
Beslenme Tipi: {nutrition.get('diet_type') if nutrition else 'Yok'}
Su: {nutrition.get('water_liters') if nutrition else 'Yok'} litre
Sebze/Meyve: {nutrition.get('vegetable_portions') if nutrition else 'Yok'} porsiyon/gün
Balık: {nutrition.get('fish_per_week') if nutrition else 'Yok'}x/hafta
İşlenmiş Gıda: {nutrition.get('processed_food_freq') if nutrition else 'Yok'}

## PERFORMANS
Antrenman: {performance.get('training_days_per_week') if performance else 'Yok'} gün/hafta
Hedef: {performance.get('goal') if performance else 'Yok'}
VO2max: {performance.get('vo2max_estimate') if performance else 'Yok'}

Aşağıdaki JSON formatında yanıt ver. Sadece JSON döndür, başka hiçbir şey yazma:

{{
  "genel_degerlendirme": "2-3 cümle genel durum özeti",
  "guclu_yonler": ["güçlü yön 1", "güçlü yön 2", "güçlü yön 3"],
  "oncelik_1": {{
    "baslik": "En kritik müdahale başlığı",
    "aciklama": "Neden önemli, 1-2 cümle",
    "adimlar": ["somut adım 1", "somut adım 2", "somut adım 3"]
  }},
  "oncelik_2": {{
    "baslik": "İkinci öncelik başlığı",
    "aciklama": "Neden önemli, 1-2 cümle",
    "adimlar": ["somut adım 1", "somut adım 2", "somut adım 3"]
  }},
  "oncelik_3": {{
    "baslik": "Üçüncü öncelik başlığı",
    "aciklama": "Neden önemli, 1-2 cümle",
    "adimlar": ["somut adım 1", "somut adım 2", "somut adım 3"]
  }},
  "motivasyon_mesaji": "Kişiye özel, samimi ve motive edici 1-2 cümle"
}}
"""

def analyze_with_ai(profile, health, lifestyle, nutrition, performance, scores, flags) -> dict:
    try:
        
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)
        prompt = build_prompt(profile, health, lifestyle, nutrition, performance, scores, flags)

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        # JSON temizle
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        return json.loads(raw)

    # except Exception as e:
    #     return {
    #         "genel_degerlendirme": "Analiz tamamlandı. Detaylar aşağıda.",
    #         "guclu_yonler": ["Değerlendirme formu dolduruldu", "Sağlık takibine başlandı"],
    #         "oncelik_1": {
    #             "baslik": "Verilerini incele",
    #             "aciklama": "Skorlarına göre en düşük alan önceliklendirildi.",
    #             "adimlar": ["Detaylı raporu incele", "Planını oluştur"]
    #         },
    #         "oncelik_2": {"baslik": "—", "aciklama": "—", "adimlar": []},
    #         "oncelik_3": {"baslik": "—", "aciklama": "—", "adimlar": []},
    #         "motivasyon_mesaji": "Her adım önemli. Devam et!"
    #     }
    except Exception as e:
        st.error(f"AI Hata: {str(e)}")
        return {
            "genel_degerlendirme": f"Hata: {str(e)}",
            "guclu_yonler": [],
            "oncelik_1": {"baslik": "—", "aciklama": "—", "adimlar": []},
            "oncelik_2": {"baslik": "—", "aciklama": "—", "adimlar": []},
            "oncelik_3": {"baslik": "—", "aciklama": "—", "adimlar": []},
            "motivasyon_mesaji": "—"
        }