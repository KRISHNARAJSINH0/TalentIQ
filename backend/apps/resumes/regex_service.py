import re
import time
import logging
from django.utils import timezone
from .models import Resume

logger = logging.getLogger(__name__)


class RegexExtractionService:
    """
    Service to perform regular expression based extraction of deterministic
    personal information, URLs, address, and zip codes from normalized resume text.
    """

    # Email regex (Gmail, Outlook, Yahoo, custom domains)
    EMAIL_REGEX = re.compile(
        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    )

    # Phone regex supporting Indian, US, and international formats with spaces, hyphens, and parens
    PHONE_REGEX = re.compile(
        r'(?:\+?\d{1,4}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}'
    )

    # Clean URL matches (not preceded by @ to avoid capturing email domains)
    URL_REGEX = re.compile(
        r'(?<!@)\b(?:https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b(?:/[^\s]*)?|(?<!@)\b[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|mil|dev|io|co|in|me|info|biz)\b(?:/[^\s]*)?'
    )

    # Pincode / ZIP Code (US Zip 5 or 5+4, Indian Pincode 6 digits)
    ZIP_REGEX = re.compile(
        r'\b\d{5}(?:-\d{4})?\b|\b\d{6}\b'
    )

    def extract_and_save(self, resume: Resume) -> bool:
        """
        Runs regex analysis on the resume's extracted_text, updates the
        model fields, and returns True on success, False on failure.
        """
        start_time = time.time()
        resume.regex_status = Resume.RegexStatus.PROCESSING
        resume.save(update_fields=["regex_status"])

        logger.info(f"Starting regex analysis for resume: {resume.id}")

        text = resume.extracted_text
        if not text or not text.strip():
            logger.warning(f"No extracted text found for resume: {resume.id}")
            self._handle_failure(resume, "No text content available for analysis.", start_time)
            return False

        try:
            # Check length safety (capping at 100 pages of typical char count, e.g., 500k chars)
            if len(text) > 500000:
                logger.warning(f"Extremely large text content for resume: {resume.id}")
                text = text[:500000]

            extracted_data = self.analyze_text(text)

            duration = time.time() - start_time
            resume.regex_json = extracted_data
            resume.regex_status = Resume.RegexStatus.COMPLETED
            resume.regex_completed_at = timezone.now()
            resume.regex_processing_time = round(duration, 4)
            resume.save(
                update_fields=[
                    "regex_json",
                    "regex_status",
                    "regex_completed_at",
                    "regex_processing_time"
                ]
            )

            logger.info(f"Successfully completed regex analysis for resume {resume.id} in {duration:.4f}s")
            return True

        except Exception as e:
            logger.error(f"Regex extraction failed for resume {resume.id}: {str(e)}", exc_info=True)
            self._handle_failure(resume, f"Extraction failed: {str(e)}", start_time)
            return False

    def analyze_text(self, text: str) -> dict:
        """
        Parses text and extracts all fields, returning a normalized dictionary.
        """
        # 1. Emails
        emails = self.EMAIL_REGEX.findall(text)
        emails = self._clean_duplicates(emails)
        
        primary_email = emails[0] if emails else None
        secondary_emails = emails[1:] if len(emails) > 1 else []

        # 2. Phones
        raw_phones = self.PHONE_REGEX.findall(text)
        phones = []
        for p in raw_phones:
            normalized = self._normalize_phone(p)
            if normalized:
                phones.append(normalized)
        phones = self._clean_duplicates(phones)

        primary_phone = phones[0] if phones else None
        secondary_phones = phones[1:] if len(phones) > 1 else []

        # 3. URLs & Profiles
        raw_urls = self.URL_REGEX.findall(text)
        normalized_urls = []
        for u in raw_urls:
            # Clean trailing punctuation commonly captured at the end of sentences
            u_clean = u.rstrip(".,;!)'\"")
            normalized = self._normalize_url(u_clean)
            if normalized:
                normalized_urls.append(normalized)
        normalized_urls = self._clean_duplicates(normalized_urls)

        # Categorize URLs
        linkedin_url = None
        github_url = None
        stackoverflow_url = None
        kaggle_url = None
        medium_url = None
        twitter_url = None
        portfolio_url = None
        personal_website = None
        other_urls = []

        for url in normalized_urls:
            url_lower = url.lower()
            if "linkedin.com" in url_lower:
                if not linkedin_url:
                    linkedin_url = url
                else:
                    other_urls.append(url)
            elif "github.com" in url_lower:
                if not github_url:
                    github_url = url
                else:
                    other_urls.append(url)
            elif "stackoverflow.com" in url_lower:
                if not stackoverflow_url:
                    stackoverflow_url = url
                else:
                    other_urls.append(url)
            elif "kaggle.com" in url_lower:
                if not kaggle_url:
                    kaggle_url = url
                else:
                    other_urls.append(url)
            elif "medium.com" in url_lower:
                if not medium_url:
                    medium_url = url
                else:
                    other_urls.append(url)
            elif "twitter.com" in url_lower or "x.com" in url_lower:
                if not twitter_url:
                    twitter_url = url
                else:
                    other_urls.append(url)
            else:
                # Distinguish between portfolio, personal, and other
                if "portfolio" in url_lower:
                    if not portfolio_url:
                        portfolio_url = url
                    else:
                        other_urls.append(url)
                elif "personal" in url_lower or "me" in url_lower or "blog" in url_lower:
                    if not personal_website:
                        personal_website = url
                    else:
                        other_urls.append(url)
                else:
                    # Heuristics for first non-social url as portfolio
                    if not portfolio_url:
                        portfolio_url = url
                    elif not personal_website:
                        personal_website = url
                    else:
                        other_urls.append(url)

        # 4. Filter text to prevent false ZIP/Address matches from emails, phones, and URLs
        clean_text = text
        for email in emails:
            clean_text = clean_text.replace(email, "")
        for phone in raw_phones:
            clean_text = clean_text.replace(phone, "")
        for url in raw_urls:
            clean_text = clean_text.replace(url, "")

        # 5. ZIP / Pincode (run on cleaned text to avoid matching phone digits)
        zips = self.ZIP_REGEX.findall(clean_text)
        zips = [self._normalize_zip(z) for z in zips]
        zips = self._clean_duplicates(zips)
        primary_zip = zips[0] if zips else None

        # 6. Address (run on cleaned text to avoid false address keywords/meta matching)
        address = self._extract_address(clean_text)

        return {
            "email": primary_email,
            "secondary_emails": secondary_emails,
            "phone": primary_phone,
            "secondary_phones": secondary_phones,
            "linkedin": linkedin_url,
            "github": github_url,
            "portfolio": portfolio_url,
            "personal_website": personal_website,
            "stackoverflow": stackoverflow_url,
            "kaggle": kaggle_url,
            "medium": medium_url,
            "twitter": twitter_url,
            "address": address,
            "pincode": primary_zip,
            "other_urls": other_urls
        }

    def _normalize_phone(self, phone_str: str) -> str:
        """Strip formatting, keep leading plus if present."""
        has_plus = phone_str.startswith("+")
        # Remove non-digits
        digits = re.sub(r'\D', '', phone_str)
        if not digits:
            return ""
        # Normalization output
        if has_plus:
            return f"+{digits}"
        # If no plus, but starts with 91 or other, let's keep it or format it
        return digits

    def _normalize_url(self, url_str: str) -> str:
        """Prepend https:// if not present and clean typical prefixes."""
        url = url_str.strip()
        if not url:
            return ""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    def _normalize_zip(self, zip_str: str) -> str:
        """Strip spaces from ZIP codes / pincodes."""
        return re.sub(r'\s', '', zip_str)

    def _extract_address(self, text: str) -> str:
        """Basic address detection based on location headers and keywords."""
        lines = text.split("\n")
        address_keywords = re.compile(
            r'\b(?:address|location|residence|residing at|permanent address|present address)\b',
            re.IGNORECASE
        )
        exclude_keywords = re.compile(
            r'\b(?:email|phone|github|linkedin|education|experience|skills|profile|objective|summary|portfolio)\b',
            re.IGNORECASE
        )

        for i, line in enumerate(lines):
            if address_keywords.search(line):
                # Clean prefix from the first line
                cleaned_line = re.sub(r'^(?:address|location|residence|residing at|permanent address|present address)\s*[:\-]\s*', '', line, flags=re.IGNORECASE).strip()
                addr_parts = []
                if cleaned_line:
                    addr_parts.append(cleaned_line)
                
                # Check next 1-2 lines for address details (cities, zip codes, states, etc.)
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not exclude_keywords.search(next_line):
                        addr_parts.append(next_line)
                
                if addr_parts:
                    return " ".join(addr_parts).strip()

        # Heuristic: search for lines containing both a zip/pincode and common state/city patterns
        return None

    def _clean_duplicates(self, items: list) -> list:
        """Remove duplicates while maintaining order."""
        seen = set()
        cleaned = []
        for item in items:
            if item.lower() not in seen:
                seen.add(item.lower())
                cleaned.append(item)
        return cleaned

    def _handle_failure(self, resume: Resume, error_message: str, start_time: float):
        """Update model fields on failure."""
        duration = time.time() - start_time
        resume.regex_status = Resume.RegexStatus.FAILED
        resume.regex_processing_time = round(duration, 4)
        resume.regex_completed_at = timezone.now()
        # We can store the error in regex_json for visibility
        resume.regex_json = {"error": error_message}
        resume.save(
            update_fields=[
                "regex_status",
                "regex_processing_time",
                "regex_completed_at",
                "regex_json"
            ]
        )
