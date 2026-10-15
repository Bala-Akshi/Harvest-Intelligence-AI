"""Bilingual core navigation and controls; original crop names are preserved."""
LABELS = {
 "Home": "முகப்பு", "Upload Data": "தரவைப் பதிவேற்று", "Dashboard": "தரவுப் பலகை",
 "Surplus and Risk": "உபரி மற்றும் அபாயம்", "Buyer Matching": "வாங்குபவர் பொருத்தம்",
 "Profit Analysis": "லாபப் பகுப்பாய்வு", "AI Assistant": "செயற்கை நுண்ணறிவு உதவியாளர்",
 "Load demo data": "மாதிரித் தரவை ஏற்று", "Validate and activate": "சரிபார்த்து பயன்படுத்து",
 "Uploaded records": "பதிவேற்றிய பதிவுகள்", "Available (kg)": "கிடைக்கும் அளவு (கிலோ)",
 "Estimated demand (kg)": "மதிப்பிடப்பட்ட தேவை (கிலோ)",
 "Potential surplus (kg)": "சாத்தியமான உபரி (கிலோ)", "Shortage (kg)": "பற்றாக்குறை (கிலோ)",
 "Navigation": "வழிசெலுத்தல்", "Save local snapshot": "உள்ளூரில் தரவைச் சேமி",
 "Restore local snapshot": "சேமித்த தரவை மீட்டெடு",
 "Upload agriculture CSV": "வேளாண் CSV கோப்பைப் பதிவேற்று",
 "Column mapping": "நெடுவரிசைப் பொருத்தம்", "Quality summary": "தரவுத் தரச் சுருக்கம்",
 "Active validated data": "சரிபார்க்கப்பட்ட நடப்புத் தரவு",
 "Download agriculture sample": "வேளாண் மாதிரியைப் பதிவிறக்கு",
 "Download buyers sample": "வாங்குபவர் மாதிரியைப் பதிவிறக்கு",
}

def label(text, language):
    return f"{LABELS.get(text, text)} · {text}" if language == "தமிழ்" else text
