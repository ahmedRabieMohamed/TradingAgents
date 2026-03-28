"""Static EGX ticker-to-company-name mapping for news search."""

# EGX30 + key EGX70 tickers mapped to English and Arabic company names.
# Used to search news by company name when given a ticker symbol.
# Update quarterly — EGX30 composition rarely changes.

EGX_TICKERS = {
    "COMI": {
        "name_en": "Commercial International Bank (CIB)",
        "name_ar": "البنك التجاري الدولي",
        "sector": "Banking",
    },
    "HRHO": {
        "name_en": "EFG Holding",
        "name_ar": "إي إف جي القابضة",
        "sector": "Financial Services",
    },
    "TMGH": {
        "name_en": "Talaat Moustafa Group",
        "name_ar": "مجموعة طلعت مصطفى",
        "sector": "Real Estate",
    },
    "EFIH": {
        "name_en": "EFG Hermes",
        "name_ar": "هيرميس",
        "sector": "Financial Services",
    },
    "SWDY": {
        "name_en": "Elsewedy Electric",
        "name_ar": "السويدي إليكتريك",
        "sector": "Industrials",
    },
    "EAST": {
        "name_en": "Eastern Company",
        "name_ar": "الشرقية إيسترن كومباني",
        "sector": "Consumer",
    },
    "ORWE": {
        "name_en": "Oriental Weavers",
        "name_ar": "النساجون الشرقيون",
        "sector": "Consumer",
    },
    "PHDC": {
        "name_en": "Palm Hills Development",
        "name_ar": "بالم هيلز للتعمير",
        "sector": "Real Estate",
    },
    "MNHD": {
        "name_en": "Madinet Nasr Housing",
        "name_ar": "مدينة نصر للإسكان",
        "sector": "Real Estate",
    },
    "EKHO": {
        "name_en": "Edita Food Industries",
        "name_ar": "إيديتا للصناعات الغذائية",
        "sector": "Consumer",
    },
    "ABUK": {
        "name_en": "Abu Qir Fertilizers",
        "name_ar": "أبو قير للأسمدة",
        "sector": "Chemicals",
    },
    "ETEL": {
        "name_en": "Telecom Egypt",
        "name_ar": "المصرية للاتصالات",
        "sector": "Telecom",
    },
    "OCDI": {
        "name_en": "Orascom Development",
        "name_ar": "أوراسكوم للتنمية",
        "sector": "Real Estate",
    },
    "ORAS": {
        "name_en": "Orascom Construction",
        "name_ar": "أوراسكوم للإنشاءات",
        "sector": "Construction",
    },
    "CCAP": {
        "name_en": "Cleopatra Hospital Group",
        "name_ar": "مجموعة مستشفيات كليوباترا",
        "sector": "Healthcare",
    },
    "JUFO": {
        "name_en": "Juhayna Food Industries",
        "name_ar": "جهينة للصناعات الغذائية",
        "sector": "Consumer",
    },
    "FWRY": {
        "name_en": "Fawry for Banking Technology",
        "name_ar": "فوري لتكنولوجيا البنوك",
        "sector": "Fintech",
    },
    "AMOC": {
        "name_en": "Alexandria Mineral Oils Company",
        "name_ar": "الإسكندرية للزيوت المعدنية",
        "sector": "Energy",
    },
    "AUTO": {
        "name_en": "GB Auto",
        "name_ar": "جي بي أوتو",
        "sector": "Automotive",
    },
    "HELI": {
        "name_en": "Heliopolis Housing",
        "name_ar": "مصر الجديدة للإسكان",
        "sector": "Real Estate",
    },
    "SKPC": {
        "name_en": "Sidi Kerir Petrochemicals",
        "name_ar": "سيدي كرير للبتروكيماويات",
        "sector": "Chemicals",
    },
    "ESRS": {
        "name_en": "Ezz Steel",
        "name_ar": "حديد عز",
        "sector": "Steel",
    },
    "ISPH": {
        "name_en": "Egyptian Starch & Glucose",
        "name_ar": "النشا والجلوكوز المصرية",
        "sector": "Consumer",
    },
    "MTIE": {
        "name_en": "Emaar Misr",
        "name_ar": "إعمار مصر",
        "sector": "Real Estate",
    },
    "EKHOA": {
        "name_en": "El Khair for Trade",
        "name_ar": "الخير للتجارة",
        "sector": "Consumer",
    },
    "BINV": {
        "name_en": "Beltone Financial",
        "name_ar": "بلتون المالية القابضة",
        "sector": "Financial Services",
    },
    "CIEB": {
        "name_en": "Credit Agricole Egypt",
        "name_ar": "كريدي أجريكول مصر",
        "sector": "Banking",
    },
    "AIIB": {
        "name_en": "Arab Investment Bank",
        "name_ar": "بنك الاستثمار العربي",
        "sector": "Banking",
    },
    "ADIB": {
        "name_en": "Abu Dhabi Islamic Bank Egypt",
        "name_ar": "مصرف أبوظبي الإسلامي مصر",
        "sector": "Banking",
    },
    "SPMD": {
        "name_en": "Speed Medical",
        "name_ar": "سبيد ميديكال",
        "sector": "Healthcare",
    },
}


def get_company_names(ticker: str) -> dict:
    """Get company names for a ticker. Returns dict with name_en, name_ar, sector.

    If ticker not found, returns generic names based on the ticker symbol.
    """
    # Strip .CA suffix if present
    clean_ticker = ticker.upper().replace(".CA", "")

    if clean_ticker in EGX_TICKERS:
        return EGX_TICKERS[clean_ticker]

    # Fallback: use ticker as company name
    return {
        "name_en": clean_ticker,
        "name_ar": clean_ticker,
        "sector": "Unknown",
    }
