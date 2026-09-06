import re
from collections import Counter

COMMON_RESUME_WORDS = {
    "resume", "curriculum", "vitae", "experience", "work", "worked", "using",
    "used", "project", "projects", "responsible", "responsibilities", "team",
    "role", "including", "etc", "year", "years", "month", "months", "company",
    "university", "college", "student", "email", "phone", "linkedin", "github",
}

EXPECTED_SECTIONS = {
    "summary": ("summary", "objective", "profile", "about me"),
    "experience": ("experience", "employment", "work history", "professional experience"),
    "education": ("education", "academic background", "qualification"),
    "skills": ("skills", "technical skills", "core competencies", "technologies"),
    "projects": ("projects", "project experience"),
}


def _words(text):
    return re.findall(r"[a-zA-Z][a-zA-Z+#.-]{2,}", text.lower())


def _contains_any(text, phrases):
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def _keyword_terms(job_description):
    words = [word for word in _words(job_description) if word not in COMMON_RESUME_WORDS]
    return {word for word in words if len(word) > 2}


def repeated_words(text, limit=8):
    words = [word for word in _words(text) if word not in COMMON_RESUME_WORDS]
    counts = Counter(words)
    return [(word, count) for word, count in counts.most_common() if count >= 4][:limit]


def analyze_resume(job_description, resume_text):
    """Return ATS signals and plain-language resume recommendations."""
    resume_words = set(_words(resume_text))
    keywords = _keyword_terms(job_description)
    matched = sorted(keywords & resume_words)
    missing = sorted(keywords - resume_words)
    keyword_score = round((len(matched) / len(keywords)) * 100) if keywords else 0

    sections = {
        section: _contains_any(resume_text, aliases)
        for section, aliases in EXPECTED_SECTIONS.items()
    }
    section_score = round(sum(sections.values()) / len(sections) * 100)

    contact_checks = {
        "email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text)),
        "phone": bool(re.search(r"(?:\+?\d[\d ()-]{7,}\d)", resume_text)),
        "profile link": bool(re.search(r"(?:linkedin\.com|github\.com|portfolio)", resume_text, re.I)),
    }
    contact_score = round(sum(contact_checks.values()) / len(contact_checks) * 100)
    word_count = len(_words(resume_text))

    score = round(keyword_score * 0.55 + section_score * 0.25 + contact_score * 0.20)
    suggestions = []
    if missing:
        suggestions.append(
            "Add evidence for job terms: " + ", ".join(missing[:8]) + ". Only include skills you genuinely have."
        )
    absent_sections = [name.title() for name, present in sections.items() if not present]
    if absent_sections:
        suggestions.append("Add clear sections for: " + ", ".join(absent_sections) + ".")
    absent_contact = [name.title() for name, present in contact_checks.items() if not present]
    if absent_contact:
        suggestions.append("Add a professional " + ", ".join(absent_contact) + " to improve recruiter reachability.")
    if word_count < 180:
        suggestions.append("Add 2-4 quantified achievement bullets so the resume has enough searchable evidence.")
    elif word_count > 900:
        suggestions.append("Trim older or low-impact content; a focused resume is easier for ATS and recruiters to scan.")
    if not re.search(r"\d", resume_text):
        suggestions.append("Add measurable outcomes such as percentages, time saved, revenue, scale, or users served.")

    repeats = repeated_words(resume_text)
    if repeats:
        top_repeats = ", ".join(f"{word} ({count}x)" for word, count in repeats[:5])
        suggestions.append("Vary or remove repeated wording: " + top_repeats + ".")

    return {
        "ats_score": score,
        "keyword_score": keyword_score,
        "section_score": section_score,
        "contact_score": contact_score,
        "word_count": word_count,
        "matched_keywords": matched,
        "missing_keywords": missing[:20],
        "sections": sections,
        "contact_checks": contact_checks,
        "repeated_words": repeats,
        "suggestions": suggestions,
    }
