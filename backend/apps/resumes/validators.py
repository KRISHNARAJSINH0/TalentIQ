import os
import zipfile
from django.core.exceptions import ValidationError

# Define constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_FILE_SIZE = 1024  # 1 KB
ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}


def validate_resume_file(uploaded_file):
    """
    Validates an uploaded resume file.
    Checks:
    - Non-empty file
    - File extension (.pdf, .docx)
    - MIME type (via uploaded_file.content_type)
    - File size (1KB - 10MB)
    - Integrity/corruption checks (PDF header check, Zipfile check for docx)
    """
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    
    # 1. Check Extension
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file extension '{ext}'. Only PDF (.pdf) and Word (.docx) files are allowed."
        )

    # 2. Check File Size
    file_size = uploaded_file.size
    if file_size is None or file_size == 0:
        raise ValidationError("The uploaded file is empty.")
    
    if file_size < MIN_FILE_SIZE:
        raise ValidationError(
            f"File is too small ({file_size} bytes). Minimum required size is 1 KB."
        )
        
    if file_size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File is too large ({file_size / (1024*1024):.2f} MB). Maximum allowed size is 10 MB."
        )

    # 3. Check MIME Type (basic check from content_type)
    mime_type = uploaded_file.content_type
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"Invalid MIME type '{mime_type}'. Only PDF and Word documents are allowed."
        )

    # 4. Corruption / Integrity checks
    try:
        # Seek to start
        uploaded_file.seek(0)
        file_header = uploaded_file.read(1024)
        
        if ext == '.pdf':
            # Check PDF Magic Header %PDF-
            if not file_header.startswith(b'%PDF'):
                raise ValidationError("The file appears to be corrupted or is not a valid PDF.")
                
        elif ext == '.docx':
            # Check if it's a valid zip file
            uploaded_file.seek(0)
            if not zipfile.is_zipfile(uploaded_file):
                raise ValidationError("The file appears to be corrupted or is not a valid DOCX document.")
                
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error validating file integrity: {str(e)}")
    finally:
        # Reset file pointer for further reading/saving
        uploaded_file.seek(0)

    return True
