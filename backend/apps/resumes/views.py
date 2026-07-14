import logging
import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Resume, ResumeSection, ConfidenceScore
from .serializers import ResumeSerializer, ResumeUploadSerializer
from .services import ResumeExtractionService
from .regex_service import RegexExtractionService
from .spacy_service import SpacyExtractionService
from .ai_service import AIResumeParserService
from .validation_service import MasterResumeBuilder

logger = logging.getLogger("apps.resumes")


class ResumeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Resumes.
    Provides endpoints for:
    - Listing resumes (GET /api/resumes/)
    - Specific details (GET /api/resumes/{id}/)
    - Soft delete (DELETE /api/resumes/{id}/)
    - Custom secure download (GET /api/resumes/{id}/download/)
    - Set active resume (PATCH /api/resumes/{id}/activate/)
    - Version history list (GET /api/resumes/history/)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own, non-deleted resumes
        return Resume.objects.filter(user=self.request.user, is_deleted=False).order_by("-upload_date")

    def get_serializer_class(self):
        if self.action == "upload":
            return ResumeUploadSerializer
        return ResumeSerializer

    def list(self, request, *args, **kwargs):
        # Standard list defaults to showing active resumes first, or sorted by upload_date
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        """
        Securely upload and validate a new resume file.
        Accepts multipart/form-data.
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                resume = serializer.save()
                logger.info(
                    f"User '{request.user.username}' successfully uploaded resume ID '{resume.id}' "
                    f"as version {resume.version}."
                )
                return Response(
                    {
                        "message": "Upload successful.",
                        "id": resume.id,
                        "filename": resume.original_filename,
                        "version": resume.version,
                        "upload_date": resume.upload_date,
                        "status": resume.upload_status,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(
                    f"Storage failure for user '{request.user.username}' during upload: {str(e)}"
                )
                return Response(
                    {"detail": f"Database or storage failure: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            logger.warning(
                f"Validation failure for user '{request.user.username}' during upload: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """
        Securely download the authenticated user's own resume.
        Prevents path traversal by utilizing Django's model file paths.
        """
        resume = get_object_or_404(Resume, pk=pk, is_deleted=False)
        
        # Security: Prevent accessing other users' resumes
        if resume.user != request.user:
            logger.warning(
                f"Unauthorized download attempt on resume '{pk}' by user '{request.user.username}'"
            )
            raise PermissionDenied("You do not have permission to download this resume.")

        file_path = resume.original_file.path
        if not os.path.exists(file_path):
            logger.error(f"Resume file path '{file_path}' does not exist on disk.")
            raise Http404("Resume file not found on server.")

        logger.info(f"User '{request.user.username}' downloaded resume ID '{resume.id}'")
        
        # Return secure FileResponse
        response = FileResponse(open(file_path, "rb"), content_type=resume.mime_type)
        response["Content-Disposition"] = f'attachment; filename="{resume.original_filename}"'
        return response

    @action(detail=True, methods=["patch"], url_path="activate")
    def activate(self, request, pk=None):
        """
        Activate a specific resume version for the user.
        Deactivates all other versions automatically.
        """
        resume = get_object_or_404(Resume, pk=pk, user=request.user, is_deleted=False)
        resume.is_active = True
        resume.save()
        
        logger.info(
            f"User '{request.user.username}' activated resume ID '{resume.id}' (v{resume.version})"
        )
        return Response(
            {"message": f"Resume version {resume.version} is now active."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """
        Retrieve paginated upload history of all resumes for the user.
        """
        queryset = self.get_queryset().order_by("-version")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ResumeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ResumeSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Perform a soft delete of the resume.
        """
        resume = self.get_object()
        
        # Perform soft delete using inheritance from SoftDeleteModel
        resume.soft_delete()
        
        logger.info(f"User '{request.user.username}' soft deleted resume ID '{resume.id}'")
        return Response(
            {"message": "Resume successfully deleted."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="extract")
    def extract(self, request, pk=None):
        """
        Triggers text extraction for this resume.
        """
        resume = self.get_object()
        service = ResumeExtractionService()
        success = service.extract_resume_text(resume)
        
        # Reload from DB to get the latest status and fields
        resume.refresh_from_db()
        
        status_code = status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
        return Response(
            {
                "resume_id": str(resume.id),
                "status": resume.extraction_status,
                "processing_time": resume.processing_duration,
                "text_length": len(resume.extracted_text) if resume.extracted_text else 0,
                "extraction_date": resume.extraction_time,
                "error_message": resume.error_message,
            },
            status=status_code
        )

    @action(detail=True, methods=["get"], url_path="text")
    def text(self, request, pk=None):
        """
        Retrieves the raw extracted text of this resume.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "extracted_text": resume.extracted_text,
        })

    @action(detail=True, methods=["get"], url_path="status")
    def status_info(self, request, pk=None):
        """
        Retrieves the extraction status metadata for this resume.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "status": resume.extraction_status,
            "processing_time": resume.processing_duration,
            "text_length": len(resume.extracted_text) if resume.extracted_text else 0,
            "extraction_date": resume.extraction_time,
            "error_message": resume.error_message,
        })

    @action(detail=True, methods=["post", "get"], url_path="regex")
    def regex(self, request, pk=None):
        """
        POST: Triggers regex analysis/extraction for this resume.
        GET: Retrieves the current extracted regex JSON data for this resume.
        """
        resume = self.get_object()
        if request.method == "POST":
            service = RegexExtractionService()
            success = service.extract_and_save(resume)
            resume.refresh_from_db()
            status_code = status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
            return Response(
                {
                    "resume_id": str(resume.id),
                    "status": resume.regex_status,
                    "processing_time": resume.regex_processing_time,
                    "completed_at": resume.regex_completed_at,
                    "regex_json": resume.regex_json,
                },
                status=status_code
            )
        else: # GET
            return Response({
                "resume_id": str(resume.id),
                "regex_json": resume.regex_json,
            })

    @action(detail=True, methods=["get"], url_path="regex/status")
    def regex_status(self, request, pk=None):
        """
        Retrieves the regex extraction status metadata for this resume.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "status": resume.regex_status,
            "processing_time": resume.regex_processing_time,
            "completed_at": resume.regex_completed_at,
        })

    @action(detail=True, methods=["post", "get"], url_path="spacy")
    def spacy(self, request, pk=None):
        """
        POST: Triggers spaCy NLP analysis/extraction for this resume.
        GET: Retrieves the current extracted spaCy JSON data for this resume.
        """
        resume = self.get_object()
        if request.method == "POST":
            service = SpacyExtractionService()
            success = service.extract_and_save(resume)
            resume.refresh_from_db()
            status_code = status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
            error_msg = None
            if not success:
                error_msg = resume.spacy_json.get("error") if isinstance(resume.spacy_json, dict) else "spaCy analysis failed."
            return Response(
                {
                    "resume_id": str(resume.id),
                    "status": resume.spacy_status,
                    "processing_time": resume.spacy_processing_time,
                    "completed_at": resume.spacy_completed_at,
                    "spacy_json": resume.spacy_json,
                    "error_message": error_msg,
                },
                status=status_code
            )
        else: # GET
            return Response({
                "resume_id": str(resume.id),
                "spacy_json": resume.spacy_json,
            })

    @action(detail=True, methods=["get"], url_path="spacy/status")
    def spacy_status(self, request, pk=None):
        """
        Retrieves the spaCy extraction status metadata for this resume.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "status": resume.spacy_status,
            "processing_time": resume.spacy_processing_time,
            "completed_at": resume.spacy_completed_at,
        })

    @action(detail=True, methods=["post", "get"], url_path="ai")
    def ai(self, request, pk=None):
        """
        POST: Triggers Gemini AI parsing/extraction for this resume.
        GET: Retrieves the current extracted AI JSON data for this resume.
        """
        resume = self.get_object()
        if request.method == "POST":
            service = AIResumeParserService()
            success = service.parse_and_save(resume)
            resume.refresh_from_db()
            status_code = status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
            error_msg = None
            if not success:
                error_msg = resume.ai_json.get("error") if isinstance(resume.ai_json, dict) else "AI parsing failed."
            return Response(
                {
                    "resume_id": str(resume.id),
                    "status": resume.ai_status,
                    "processing_time": resume.ai_processing_time,
                    "completed_at": resume.ai_completed_at,
                    "ai_model": resume.ai_model,
                    "ai_prompt_version": resume.ai_prompt_version,
                    "ai_json": resume.ai_json,
                    "error_message": error_msg,
                },
                status=status_code
            )
        else: # GET
            return Response({
                "resume_id": str(resume.id),
                "ai_json": resume.ai_json,
            })

    @action(detail=True, methods=["get"], url_path="ai/status")
    def ai_status(self, request, pk=None):
        """
        Retrieves the Gemini AI extraction status metadata for this resume.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "status": resume.ai_status,
            "processing_time": resume.ai_processing_time,
            "completed_at": resume.ai_completed_at,
            "ai_model": resume.ai_model,
            "ai_prompt_version": resume.ai_prompt_version,
        })

    @action(detail=True, methods=["post"], url_path="merge")
    def merge(self, request, pk=None):
        """
        Combines intermediate parsed outputs (Regex, spaCy, Gemini) into one master profile.
        """
        resume = self.get_object()
        builder = MasterResumeBuilder()
        success = builder.build_master_profile(resume)
        
        resume.refresh_from_db()
        status_code = status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
        return Response({
            "resume_id": str(resume.id),
            "validation_status": resume.validation_status,
            "validation_time": resume.validation_time,
            "completion_percentage": resume.completion_percentage,
            "master_resume_json": resume.master_resume_json,
        }, status=status_code)

    @action(detail=True, methods=["get"], url_path="master")
    def master(self, request, pk=None):
        """
        Retrieves the master resume JSON profile.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "validation_status": resume.validation_status,
            "validation_time": resume.validation_time,
            "master_resume_json": resume.master_resume_json,
        })

    @action(detail=True, methods=["get"], url_path="completion")
    def completion(self, request, pk=None):
        """
        Retrieves the completion status and overall percentage.
        """
        resume = self.get_object()
        return Response({
            "resume_id": str(resume.id),
            "validation_status": resume.validation_status,
            "completion_percentage": resume.completion_percentage,
        })


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import ResumeSectionSerializer
from .services.section_detector import SectionDetector


class ResumeSectionDetectionView(APIView):
    """
    POST: /api/resume/sections/
    Returns structured resume sections, page mapping, confidence scores, and layout type.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        resume_id = request.data.get("resume_id")
        raw_text = request.data.get("text")

        if not resume_id and not raw_text:
            return Response(
                {"detail": "Either 'resume_id' or 'text' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        detector = SectionDetector()

        if resume_id:
            # Fetch user resume
            resume = get_object_or_404(Resume, id=resume_id, user=request.user, is_deleted=False)
            
            # Detect sections and persist to database
            result = detector.detect_and_save(resume)
            
            # Serialize the saved sections
            sections = resume.sections.all().order_by("position")
            sections_data = []
            for sec in sections:
                sections_data.append({
                    "id": str(sec.id),
                    "type": sec.section_type,
                    "title": sec.title,
                    "content": sec.content,
                    "confidence": sec.confidence,
                    "position": sec.position,
                    "page": sec.page
                })
            
            return Response({
                "layout": result.get("layout", "single_column"),
                "sections": sections_data
            }, status=status.HTTP_200_OK)

        else:
            # Parse raw text (not persisted in DB)
            result = detector.detect_sections(raw_text)
            sections_data = []
            for sec in result.get("sections", []):
                sections_data.append({
                    "type": sec.get("type"),
                    "title": sec.get("title"),
                    "content": sec.get("content"),
                    "confidence": sec.get("confidence", 100.0),
                    "page": sec.get("page", 1)
                })
            return Response({
                "layout": result.get("layout", "single_column"),
                "sections": sections_data
            }, status=status.HTTP_200_OK)


from .serializers import ConfidenceScoreSerializer
from .services.confidence_engine import ConfidenceEngine


class ResumeConfidenceView(APIView):
    """
    POST: /api/resume/confidence/
    Calculates and saves confidence scores for the given resume_id.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"detail": "Parameter 'resume_id' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user, is_deleted=False)

        # Ensure validation/merge has run
        if not resume.master_resume_json:
            from .validation_service import MasterResumeBuilder
            builder = MasterResumeBuilder()
            builder.build_master_profile(resume)
            resume.refresh_from_db()

        engine = ConfidenceEngine()
        result_map = engine.evaluate_and_save(resume)

        # Retrieve saved scores
        scores = ConfidenceScore.objects.filter(resume=resume).order_by("field")
        serializer = ConfidenceScoreSerializer(scores, many=True)

        return Response({
            "resume_id": str(resume.id),
            "fields": serializer.data,
            "confidence_map": result_map
        }, status=status.HTTP_200_OK)


class ResumeConfidenceDetailView(APIView):
    """
    GET: /api/resume/confidence/{id}
    Retrieves saved confidence scores for a resume by ID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        resume = get_object_or_404(Resume, id=pk, user=request.user, is_deleted=False)
        scores = ConfidenceScore.objects.filter(resume=resume).order_by("field")
        
        # Serialize scores
        serializer = ConfidenceScoreSerializer(scores, many=True)
        
        # Build dictionary map
        confidence_map = {}
        for s in scores:
            confidence_map[s.field] = {
                "value": s.value,
                "confidence": s.confidence,
                "source": s.source,
                "reason": s.reason,
                "status": s.status
            }

        return Response({
            "resume_id": str(resume.id),
            "fields": serializer.data,
            "confidence_map": confidence_map
        }, status=status.HTTP_200_OK)


from .models import SemanticValidation
from .serializers import SemanticValidationSerializer
from .services.semantic_validator import SemanticValidator


class ResumeSemanticValidationView(APIView):
    """
    POST: /api/resume/semantic/
    Validates extracted resume entities semantically, detects anomalies, calculates semantic scores (0-100),
    assigns validation status and action flags, and provides explainable rationales.
    Supports either 'resume_id' or raw entity JSON payload.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        resume_id = request.data.get("resume_id")
        raw_payload = request.data.get("payload")

        # If payload is directly top-level JSON without wrapping key
        if not raw_payload and not resume_id and isinstance(request.data, dict):
            raw_payload = request.data

        if not resume_id and not raw_payload:
            return Response(
                {"detail": "Either 'resume_id' or entity JSON payload is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        validator = SemanticValidator()

        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id, user=request.user, is_deleted=False)
            payload_to_validate = resume.master_resume_json or resume.ai_json or {}

            # Perform validation
            validation_report = validator.validate_payload(payload_to_validate)

            # Persist to database
            SemanticValidation.objects.filter(resume=resume).delete()
            saved_objects = []

            for item in validation_report["validations"]:
                obj = SemanticValidation.objects.create(
                    resume=resume,
                    field=item.get("field", "unknown"),
                    value=item.get("value", ""),
                    category=item.get("category", "Unknown"),
                    expected_category=item.get("expected_category", "Unknown"),
                    semantic_score=item.get("semantic_score", 0.0),
                    reason=item.get("reason", ""),
                    status=item.get("status", "invalid"),
                    action=item.get("action", "reject")
                )
                saved_objects.append(obj)

            serializer = SemanticValidationSerializer(saved_objects, many=True)
            return Response({
                "resume_id": str(resume.id),
                "validations": serializer.data,
                "metrics": validation_report["metrics"]
            }, status=status.HTTP_200_OK)

        else:
            # Validate raw payload directly
            validation_report = validator.validate_payload(raw_payload)
            return Response(validation_report, status=status.HTTP_200_OK)


class ResumeSemanticDetailView(APIView):
    """
    GET: /api/resume/semantic/{id}
    Retrieves semantic validation results by SemanticValidation ID or Resume UUID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # 1. Try finding by SemanticValidation PK
        val = SemanticValidation.objects.filter(id=pk).first()
        if val:
            # Check user permission if linked to resume
            if val.resume and val.resume.user != request.user:
                raise PermissionDenied("You do not have permission to access this validation record.")
            serializer = SemanticValidationSerializer(val)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. Try finding by Resume UUID
        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if resume:
            validations = SemanticValidation.objects.filter(resume=resume).order_by("-semantic_score")
            serializer = SemanticValidationSerializer(validations, many=True)
            return Response({
                "resume_id": str(resume.id),
                "validations": serializer.data,
                "count": validations.count()
            }, status=status.HTTP_200_OK)

        raise Http404("Semantic validation record or Resume not found.")


class ResumeErrorDetectionView(APIView):
    """
    POST: /api/resume/errors/ or /api/ai/errors/
    Runs the Error Detector Engine (Stage 8) against an existing Resume or raw JSON payload.
    Persists ResumeError instances if resume_id is provided.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import ResumeErrorSerializer, ResumeErrorRequestSerializer
        from .services.error_detector import ErrorDetector
        from .models import ResumeError

        req_serializer = ResumeErrorRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        raw_payload = req_serializer.validated_data.get("payload")
        confidence_map = req_serializer.validated_data.get("confidence_map")

        if not resume_id and not raw_payload:
            return Response(
                {"error": "Either 'resume_id' or 'payload' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        detector = ErrorDetector()

        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

            payload_to_test = resume.master_resume_json or {}
            error_report = detector.detect_errors(payload_to_test, confidence_map)

            # Clear old error detections for this resume
            ResumeError.objects.filter(resume=resume).delete()

            saved_errors = []
            for err in error_report["errors"]:
                obj = ResumeError.objects.create(
                    resume=resume,
                    type=err.get("type", "unknown"),
                    field=err.get("field", "general"),
                    value=str(err.get("value", "")),
                    severity=err.get("severity", "medium"),
                    confidence=float(err.get("confidence", 100.0)),
                    action=err.get("action", "review"),
                    reason=err.get("reason", "")
                )
                saved_errors.append(obj)

            serializer = ResumeErrorSerializer(saved_errors, many=True)
            return Response({
                "resume_id": str(resume.id),
                "errors": serializer.data,
                "metrics": error_report["metrics"]
            }, status=status.HTTP_200_OK)

        else:
            error_report = detector.detect_errors(raw_payload, confidence_map)
            return Response(error_report, status=status.HTTP_200_OK)


class ResumeErrorDetailView(APIView):
    """
    GET: /api/resume/errors/{id} or /api/ai/errors/{id}
    Retrieves error detection records by ResumeError ID or Resume UUID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        from .serializers import ResumeErrorSerializer
        from .models import ResumeError

        # 1. Try finding by ResumeError PK
        err_obj = ResumeError.objects.filter(id=pk).first()
        if err_obj:
            if err_obj.resume and err_obj.resume.user != request.user:
                raise PermissionDenied("You do not have permission to access this error record.")
            serializer = ResumeErrorSerializer(err_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. Try finding by Resume UUID
        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if resume:
            errors_qs = ResumeError.objects.filter(resume=resume).order_by("-created_at")
            serializer = ResumeErrorSerializer(errors_qs, many=True)
            return Response({
                "resume_id": str(resume.id),
                "errors": serializer.data,
                "count": errors_qs.count()
            }, status=status.HTTP_200_OK)

        raise Http404("Resume error record or Resume not found.")


class ResumeErrorSummaryView(APIView):
    """
    GET: /api/resume/errors/summary/ or /api/ai/errors/summary/
    Retrieves global aggregated error stats for the authenticated user's resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .models import ResumeError
        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        user_errors = ResumeError.objects.filter(resume__in=user_resumes)

        total_errors = user_errors.count()
        critical_count = user_errors.filter(severity="critical").count()
        high_count = user_errors.filter(severity="high").count()
        medium_count = user_errors.filter(severity="medium").count()
        low_count = user_errors.filter(severity="low").count()

        return Response({
            "total_user_resumes": user_resumes.count(),
            "total_errors_detected": total_errors,
            "severity_breakdown": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            }
        }, status=status.HTTP_200_OK)


class ResumeRecoveryView(APIView):
    """
    POST: /api/recovery/
    Runs AI Recovery Engine (Stage 9 / Phase 9.5) to automatically repair parser mistakes,
    relocate misplaced entities, swap inverted dates, deduplicate lists, and update master resume JSON.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import RecoveryLogSerializer, RecoveryRequestSerializer
        from .services.recovery_engine import RecoveryEngine
        from .models import RecoveryLog

        req_serializer = RecoveryRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        raw_payload = req_serializer.validated_data.get("payload")
        error_report = req_serializer.validated_data.get("error_report")
        confidence_map = req_serializer.validated_data.get("confidence_map")

        if not resume_id and not raw_payload:
            return Response(
                {"error": "Either 'resume_id' or 'payload' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        engine = RecoveryEngine()

        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

            payload_to_test = raw_payload or resume.master_resume_json or {}
            rec_result = engine.recover_payload(payload_to_test, error_report, confidence_map)

            # Update master resume JSON with recovered payload
            resume.master_resume_json = rec_result["recovered_json"]
            resume.save(update_fields=["master_resume_json"])

            # Clear old recovery logs for this resume
            RecoveryLog.objects.filter(resume=resume).delete()

            saved_logs = []
            for rec in rec_result["recoveries"]:
                obj = RecoveryLog.objects.create(
                    resume=resume,
                    field=rec.get("to") or rec.get("field") or "general",
                    previous_value=str(rec.get("from") or rec.get("value") or ""),
                    new_value=str(rec.get("value") or ""),
                    reason=rec.get("reason", ""),
                    confidence=float(rec.get("confidence", 95.0)),
                    status=rec.get("status", "recovered")
                )
                saved_logs.append(obj)

            serializer = RecoveryLogSerializer(saved_logs, many=True)
            return Response({
                "resume_id": str(resume.id),
                "recovered_json": rec_result["recovered_json"],
                "recoveries": serializer.data,
                "metrics": rec_result["metrics"]
            }, status=status.HTTP_200_OK)

        else:
            rec_result = engine.recover_payload(raw_payload, error_report, confidence_map)
            return Response(rec_result, status=status.HTTP_200_OK)


class ResumeRecoveryDetailView(APIView):
    """
    GET: /api/recovery/{id}
    Retrieves recovery logs by RecoveryLog ID or Resume UUID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        from .serializers import RecoveryLogSerializer
        from .models import RecoveryLog

        # 1. Try finding by RecoveryLog PK
        log_obj = RecoveryLog.objects.filter(id=pk).first()
        if log_obj:
            if log_obj.resume and log_obj.resume.user != request.user:
                raise PermissionDenied("You do not have permission to access this recovery record.")
            serializer = RecoveryLogSerializer(log_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. Try finding by Resume UUID
        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if resume:
            logs_qs = RecoveryLog.objects.filter(resume=resume).order_by("-created_at")
            serializer = RecoveryLogSerializer(logs_qs, many=True)
            return Response({
                "resume_id": str(resume.id),
                "recovered_json": resume.master_resume_json,
                "recoveries": serializer.data,
                "count": logs_qs.count()
            }, status=status.HTTP_200_OK)

        raise Http404("Recovery record or Resume not found.")


class ResumeRecoveryHistoryView(APIView):
    """
    GET: /api/recovery/history/
    Retrieves history of recovery operations for the authenticated user's resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import RecoveryLogSerializer
        from .models import RecoveryLog

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        user_logs = RecoveryLog.objects.filter(resume__in=user_resumes).order_by("-created_at")[:50]
        serializer = RecoveryLogSerializer(user_logs, many=True)

        return Response({
            "history_count": user_logs.count(),
            "recovery_history": serializer.data
        }, status=status.HTTP_200_OK)


class ResumeConsistencyView(APIView):
    """
    POST: /api/consistency/
    Runs Consistency Checker (Stage 9 / Phase 9.6) to validate resume coherence, timeline alignments,
    role skill gaps, project domain relevance, and section completeness.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import ConsistencyReportSerializer, ConsistencyRequestSerializer
        from .services.consistency_checker import ConsistencyChecker
        from .models import ConsistencyReport

        req_serializer = ConsistencyRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        raw_payload = req_serializer.validated_data.get("payload")

        if not resume_id and not raw_payload:
            return Response(
                {"error": "Either 'resume_id' or 'payload' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        checker = ConsistencyChecker()

        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

            payload_to_test = raw_payload or resume.master_resume_json or {}
            check_result = checker.check_consistency(payload_to_test)

            report = ConsistencyReport.objects.create(
                resume=resume,
                score=float(check_result["consistency_score"]),
                score_label=check_result["score_label"],
                issues=check_result["issues"],
                suggestions=check_result["suggestions"],
                metrics=check_result["metrics"]
            )

            serializer = ConsistencyReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            check_result = checker.check_consistency(raw_payload)
            return Response(check_result, status=status.HTTP_200_OK)


class ResumeConsistencyDetailView(APIView):
    """
    GET: /api/consistency/{id}
    Retrieves consistency report by Report ID or Resume UUID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        from .serializers import ConsistencyReportSerializer
        from .models import ConsistencyReport

        # 1. Try finding by ConsistencyReport PK
        report_obj = ConsistencyReport.objects.filter(id=pk).first()
        if report_obj:
            if report_obj.resume and report_obj.resume.user != request.user:
                raise PermissionDenied("You do not have permission to access this consistency report.")
            serializer = ConsistencyReportSerializer(report_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. Try finding by Resume UUID
        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if resume:
            reports_qs = ConsistencyReport.objects.filter(resume=resume).order_by("-created_at")
            serializer = ConsistencyReportSerializer(reports_qs, many=True)
            return Response({
                "resume_id": str(resume.id),
                "reports": serializer.data,
                "count": reports_qs.count()
            }, status=status.HTTP_200_OK)

        raise Http404("Consistency report or Resume not found.")


class ResumeConsistencyHistoryView(APIView):
    """
    GET: /api/consistency/history/
    Retrieves history of consistency audits for the authenticated user's resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import ConsistencyReportSerializer
        from .models import ConsistencyReport

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        user_reports = ConsistencyReport.objects.filter(resume__in=user_resumes).order_by("-created_at")[:50]
        serializer = ConsistencyReportSerializer(user_reports, many=True)

        return Response({
            "history_count": user_reports.count(),
            "consistency_history": serializer.data
        }, status=status.HTTP_200_OK)


class ResumeSourceView(APIView):
    """
    POST: /api/source/
    Executes Source Tracking Engine (Stage 9 / Phase 9.7) to analyze data provenance,
    source origins (Regex, spaCy, Gemini, Recovery, User Edit), UI colors, and audit trails.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import SourceTrackerRequestSerializer, FieldSourceSerializer
        from .services.provenance_engine import ProvenanceEngine
        from .models import FieldSource, FieldHistory

        req_serializer = SourceTrackerRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        raw_payload = req_serializer.validated_data.get("payload")
        engine_origins = req_serializer.validated_data.get("engine_origins")
        recoveries = req_serializer.validated_data.get("recoveries")
        old_payload = req_serializer.validated_data.get("old_payload")

        if not resume_id and not raw_payload:
            return Response(
                {"error": "Either 'resume_id' or 'payload' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        engine = ProvenanceEngine()

        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

            payload_to_test = raw_payload or resume.master_resume_json or {}
            provenance_res = engine.process_provenance(
                payload_to_test,
                engine_origins=engine_origins,
                recoveries=recoveries,
                old_payload=old_payload
            )

            # Persist FieldSource records
            saved_sources = []
            for field_name, p_info in provenance_res["provenance_map"].items():
                fs_obj, _ = FieldSource.objects.update_or_create(
                    resume=resume,
                    field=field_name,
                    version=1,
                    defaults={
                        "value": str(p_info.get("value") or ""),
                        "source": p_info.get("source", "spacy"),
                        "confidence": float(p_info.get("confidence", 90.0)),
                        "status": p_info.get("status", "extracted"),
                        "reason": str(p_info.get("reason") or ""),
                        "ui_color": p_info.get("ui_color", "#3B82F6")
                    }
                )
                saved_sources.append(fs_obj)

            serializer = FieldSourceSerializer(saved_sources, many=True)
            return Response({
                "resume_id": str(resume.id),
                "field_sources": serializer.data,
                "provenance_map": provenance_res["provenance_map"],
                "audit_summary": provenance_res["audit_summary"],
                "version_diff": provenance_res["version_diff"],
                "metrics": provenance_res["metrics"]
            }, status=status.HTTP_200_OK)

        else:
            provenance_res = engine.process_provenance(
                raw_payload,
                engine_origins=engine_origins,
                recoveries=recoveries,
                old_payload=old_payload
            )
            return Response(provenance_res, status=status.HTTP_200_OK)


class ResumeSourceDetailView(APIView):
    """
    GET: /api/source/{resume_id}
    Retrieves data provenance map and field sources for a specific resume.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        from .serializers import FieldSourceSerializer
        from .models import FieldSource

        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if not resume:
            raise Http404("Resume not found or access denied.")

        sources = FieldSource.objects.filter(resume=resume)
        serializer = FieldSourceSerializer(sources, many=True)

        return Response({
            "resume_id": str(resume.id),
            "sources": serializer.data,
            "count": sources.count()
        }, status=status.HTTP_200_OK)


class ResumeSourceHistoryView(APIView):
    """
    GET: /api/source/history/
    Retrieves history of field modifications across user's resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import FieldHistorySerializer
        from .models import FieldHistory

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        histories = FieldHistory.objects.filter(resume__in=user_resumes).order_by("-timestamp")[:50]
        serializer = FieldHistorySerializer(histories, many=True)

        return Response({
            "history_count": histories.count(),
            "field_history": serializer.data
        }, status=status.HTTP_200_OK)


class ResumeSourceAuditView(APIView):
    """
    GET: /api/source/audit/
    Retrieves full explainability audit summaries.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .services.audit_engine import AuditEngine
        from .services.source_tracker import SourceTracker

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        tracker = SourceTracker()
        audit_engine = AuditEngine()

        total_audited = 0
        all_audits = []

        for r in user_resumes[:10]:
            p_map = tracker.track_field_sources(r.master_resume_json or {})
            aud = audit_engine.audit_full_resume(p_map)
            all_audits.append({
                "resume_id": str(r.id),
                "resume_title": r.resume_title,
                "audit_summary": aud
            })
            total_audited += 1

        return Response({
            "audited_resumes_count": total_audited,
            "audits": all_audits
        }, status=status.HTTP_200_OK)


class ResumeSelfHealingView(APIView):
    """
    POST: /api/self-healing/
    Executes Self-Healing Parser Engine (Stage 9 / Phase 9.8).
    Orchestrates text extraction, section detection, multi-engine parsing,
    confidence scoring, AI recovery, consistency checking, source tracking,
    result merging, and Master Resume JSON generation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import SelfHealingRequestSerializer, SelfHealingReportSerializer
        from .services.self_healing_parser import SelfHealingParser
        from .models import SelfHealingReport

        req_serializer = SelfHealingRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        raw_payload = req_serializer.validated_data.get("payload")
        engine_origins = req_serializer.validated_data.get("engine_origins")
        user_edits = req_serializer.validated_data.get("user_edits")

        if not resume_id and not raw_payload:
            return Response(
                {"error": "Either 'resume_id' or 'payload' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        parser = SelfHealingParser()

        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

            payload_to_parse = raw_payload or resume.master_resume_json or {}
            result = parser.parse_and_heal(payload_to_parse, engine_origins=engine_origins, user_edits=user_edits)

            healing_info = result["healing_report"]
            master_resume = result["master_resume"]

            # Save report
            report = SelfHealingReport.objects.create(
                resume=resume,
                confidence=healing_info["confidence"],
                issues_found=healing_info["issues_found"],
                issues_fixed=healing_info["issues_fixed"],
                needs_review=healing_info["needs_review"],
                recovered_fields_count=healing_info.get("recovered_fields_count", 0),
                decision=healing_info["decision"],
                approval_tier=healing_info["approval_tier"],
                summary=healing_info["summary"],
                master_resume_output=master_resume
            )

            # Update resume master json
            resume.master_resume_json = master_resume
            resume.save(update_fields=["master_resume_json", "updated_at"])

            serializer = SelfHealingReportSerializer(report)
            return Response({
                "report_id": str(report.id),
                "resume_id": str(resume.id),
                "report": serializer.data,
                "master_resume": master_resume,
                "healing_report": healing_info,
                "provenance_map": result["provenance_map"],
                "consistency_summary": result["consistency_summary"],
                "pipeline_summary": result["pipeline_summary"]
            }, status=status.HTTP_200_OK)

        else:
            result = parser.parse_and_heal(raw_payload, engine_origins=engine_origins, user_edits=user_edits)
            return Response(result, status=status.HTTP_200_OK)


class ResumeSelfHealingDetailView(APIView):
    """
    GET: /api/self-healing/{id}
    Retrieves Self-Healing Report by Report ID or Resume UUID.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        from .serializers import SelfHealingReportSerializer
        from .models import SelfHealingReport

        report = SelfHealingReport.objects.filter(id=pk, resume__user=request.user).first()
        if report:
            serializer = SelfHealingReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)

        resume = Resume.objects.filter(id=pk, user=request.user, is_deleted=False).first()
        if resume:
            reports_qs = SelfHealingReport.objects.filter(resume=resume).order_by("-created_at")
            serializer = SelfHealingReportSerializer(reports_qs, many=True)
            return Response({
                "resume_id": str(resume.id),
                "reports": serializer.data,
                "count": reports_qs.count()
            }, status=status.HTTP_200_OK)

        raise Http404("Self-healing report or Resume not found.")


class ResumeSelfHealingReportView(APIView):
    """
    GET: /api/self-healing/report/
    Retrieves aggregate self-healing reports and metrics for user's resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import SelfHealingReportSerializer
        from .models import SelfHealingReport

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        reports = SelfHealingReport.objects.filter(resume__in=user_resumes).order_by("-created_at")[:50]
        serializer = SelfHealingReportSerializer(reports, many=True)

        return Response({
            "total_reports": reports.count(),
            "healing_reports": serializer.data
        }, status=status.HTTP_200_OK)


class ResumeCopilotChatView(APIView):
    """
    POST: /api/copilot/chat/
    Conversational Resume AI Assistant endpoint (Stage 9 / Phase 9.9).
    Processes user prompts ("Add Docker", "Remove Java", "My education is wrong", "Improve ATS")
    and modifies Master Resume JSON.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import CopilotChatRequestSerializer, CopilotConversationSerializer
        from .services.resume_copilot import ResumeCopilot
        from .models import CopilotConversation, CopilotAction

        req_serializer = CopilotChatRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        user_message = req_serializer.validated_data.get("message")
        raw_payload = req_serializer.validated_data.get("payload")

        resume = None
        if resume_id:
            resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
            if not resume:
                return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        master_json = raw_payload or (resume.master_resume_json if resume else {}) or {}

        copilot = ResumeCopilot()
        result = copilot.process_chat(user_message, master_json)

        # Save conversation
        conversation = CopilotConversation.objects.create(
            user=request.user,
            resume=resume,
            message=user_message,
            response=result["response"],
            intent=result["intent"]
        )

        # If master_json changed and resume exists, save state snapshot and action
        if resume and result["updated_master_json"] != master_json:
            prev_state = master_json
            new_state = result["updated_master_json"]

            CopilotAction.objects.create(
                resume=resume,
                user=request.user,
                action=result["action"],
                previous_state=prev_state,
                new_state=new_state,
                confidence=result["confidence"]
            )

            resume.master_resume_json = new_state
            resume.save(update_fields=["master_resume_json", "updated_at"])

        conv_serializer = CopilotConversationSerializer(conversation)
        return Response({
            "conversation": conv_serializer.data,
            "intent": result["intent"],
            "action": result["action"],
            "response": result["response"],
            "updated_master_json": result["updated_master_json"],
            "confidence": result["confidence"],
            "ats_summary": result["ats_summary"],
            "suggestions": result["suggestions"]
        }, status=status.HTTP_200_OK)


class ResumeCopilotActionView(APIView):
    """
    POST: /api/copilot/action/
    Executes structural copilot actions including Undo / Redo operations.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .serializers import CopilotActionRequestSerializer, CopilotActionSerializer
        from .models import CopilotAction, Resume

        req_serializer = CopilotActionRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(req_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        resume_id = req_serializer.validated_data.get("resume_id")
        action_name = req_serializer.validated_data.get("action").lower()

        resume = Resume.objects.filter(id=resume_id, user=request.user, is_deleted=False).first()
        if not resume:
            return Response({"error": "Resume not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        if action_name == "undo":
            last_action = CopilotAction.objects.filter(resume=resume, is_undone=False).order_by("-created_at").first()
            if not last_action:
                return Response({"message": "No actions to undo."}, status=status.HTTP_400_BAD_REQUEST)

            resume.master_resume_json = last_action.previous_state
            resume.save(update_fields=["master_resume_json", "updated_at"])

            last_action.is_undone = True
            last_action.save(update_fields=["is_undone"])

            return Response({
                "message": f"Successfully undone action '{last_action.action}'",
                "master_resume_json": resume.master_resume_json
            }, status=status.HTTP_200_OK)

        elif action_name == "redo":
            last_undone = CopilotAction.objects.filter(resume=resume, is_undone=True).order_by("created_at").first()
            if not last_undone:
                return Response({"message": "No actions to redo."}, status=status.HTTP_400_BAD_REQUEST)

            resume.master_resume_json = last_undone.new_state
            resume.save(update_fields=["master_resume_json", "updated_at"])

            last_undone.is_undone = False
            last_undone.save(update_fields=["is_undone"])

            return Response({
                "message": f"Successfully redone action '{last_undone.action}'",
                "master_resume_json": resume.master_resume_json
            }, status=status.HTTP_200_OK)

        return Response({"error": f"Unsupported action '{action_name}'"}, status=status.HTTP_400_BAD_REQUEST)


class ResumeCopilotHistoryView(APIView):
    """
    GET: /api/copilot/history/
    Retrieves conversation chat history for current user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import CopilotConversationSerializer
        from .models import CopilotConversation

        conversations = CopilotConversation.objects.filter(user=request.user).order_by("-created_at")[:50]
        serializer = CopilotConversationSerializer(conversations, many=True)

        return Response({
            "history_count": conversations.count(),
            "history": serializer.data
        }, status=status.HTTP_200_OK)


class ResumeCopilotSuggestionsView(APIView):
    """
    GET: /api/copilot/suggestions/
    Retrieves proactive AI recommendations for user's active resumes.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .services.suggestion_engine import SuggestionEngine

        user_resumes = Resume.objects.filter(user=request.user, is_deleted=False)
        engine = SuggestionEngine()

        all_suggestions = []
        for r in user_resumes[:10]:
            suggs = engine.generate_suggestions(r.master_resume_json or {})
            all_suggestions.append({
                "resume_id": str(r.id),
                "resume_title": r.resume_title,
                "suggestions": suggs
            })

        return Response({
            "resumes_count": len(all_suggestions),
            "suggestions": all_suggestions
        }, status=status.HTTP_200_OK)


class ResumeCopilotChangesView(APIView):
    """
    GET: /api/copilot/changes/
    Retrieves AI action change logs and execution history.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .serializers import CopilotActionSerializer
        from .models import CopilotAction

        actions = CopilotAction.objects.filter(user=request.user).order_by("-created_at")[:50]
        serializer = CopilotActionSerializer(actions, many=True)

        return Response({
            "changes_count": actions.count(),
            "changes": serializer.data
        }, status=status.HTTP_200_OK)









