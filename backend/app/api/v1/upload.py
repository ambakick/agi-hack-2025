"""Upload endpoint for multi-modal source files."""
import os
import uuid
import mimetypes
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import UploadResponse, SourceType, SourceMetadata
from app.core.config import settings

router = APIRouter()

# Create upload directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create subdirectories for each source type
for source_type in SourceType:
    (UPLOAD_DIR / source_type.value).mkdir(exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()


def validate_file_type(file: UploadFile, source_type: SourceType) -> bool:
    """Validate that uploaded file matches declared source type."""
    mime_type = file.content_type or ""
    extension = get_file_extension(file.filename or "")
    
    type_validators = {
        SourceType.PDF: lambda m, e: "pdf" in m or e == ".pdf",
        SourceType.IMAGE: lambda m, e: m.startswith("image/") or e in [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        SourceType.AUDIO: lambda m, e: m.startswith("audio/") or e in [".mp3", ".wav", ".ogg", ".m4a"],
        SourceType.VIDEO: lambda m, e: m.startswith("video/") or e in [".mp4", ".webm", ".ogg", ".mov"],
    }
    
    validator = type_validators.get(source_type)
    if not validator:
        return False
        
    return validator(mime_type, extension)


def generate_thumbnail_url(file_path: Path, source_type: SourceType) -> str:
    """Generate a thumbnail URL for the uploaded file."""
    # For now, return a placeholder or the file URL itself
    # In a real implementation, you'd generate actual thumbnails for videos/PDFs
    if source_type in [SourceType.IMAGE]:
        return f"/{file_path}"
    return ""


def get_file_metadata(file_path: Path, source_type: SourceType, original_filename: str) -> SourceMetadata:
    """Extract metadata from uploaded file."""
    file_size = file_path.stat().st_size
    mime_type = mimetypes.guess_type(str(file_path))[0] or ""
    
    metadata = SourceMetadata(
        file_size=file_size,
        mime_type=mime_type
    )
    
    # For PDFs, we could extract page count (requires PyPDF2 or similar)
    # For audio/video, we could extract duration (requires ffprobe)
    # These are left as future enhancements
    
    return metadata


@router.post("/upload", response_model=UploadResponse)
async def upload_source(
    file: UploadFile = File(...),
    source_type: str = Form(...)
) -> UploadResponse:
    """
    Upload a source file (PDF, image, audio, or video).
    
    Args:
        file: The file to upload
        source_type: Type of source (pdf, image, audio, video)
        
    Returns:
        Source information including file path and metadata
    """
    try:
        # Validate source type
        try:
            source_type_enum = SourceType(source_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source_type. Must be one of: {', '.join([t.value for t in SourceType if t != SourceType.YOUTUBE])}"
            )
        
        # Validate that file type matches declared source type
        if not validate_file_type(file, source_type_enum):
            raise HTTPException(
                status_code=400,
                detail=f"File type does not match declared source_type: {source_type}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = get_file_extension(file.filename or "")
        new_filename = f"{file_id}{file_extension}"
        
        # Determine save path
        source_dir = UPLOAD_DIR / source_type_enum.value
        file_path = source_dir / new_filename
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Generate URLs
        relative_path = f"uploads/{source_type_enum.value}/{new_filename}"
        file_url = f"/{relative_path}"
        thumbnail_url = generate_thumbnail_url(file_path, source_type_enum)
        
        # Extract metadata
        metadata = get_file_metadata(file_path, source_type_enum, file.filename or "")
        
        return UploadResponse(
            id=file_id,
            type=source_type_enum,
            name=file.filename or new_filename,
            thumbnail_url=thumbnail_url or None,
            file_path=relative_path,
            file_url=file_url,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
