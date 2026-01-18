import base64
import io
from PIL import Image


def compress_base64_image(base64_string, max_width=400, quality=85):
    """
    Compress a base64 encoded image by resizing and reducing quality.
    
    Args:
        base64_string (str): Base64 encoded image string (with or without data URI prefix)
        max_width (int): Maximum width for the compressed image (default: 400px)
        quality (int): JPEG quality (1-100, default: 85)
    
    Returns:
        str: Compressed base64 encoded image string with data URI prefix
    
    Raises:
        ValueError: If the input is not a valid base64 image
    """
    try:
        # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_string:
            header, base64_data = base64_string.split(',', 1)
        else:
            base64_data = base64_string
        
        # Always use JPEG header since we're converting to JPEG
        header = "data:image/jpeg;base64"
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        original_width, original_height = image.size
        if original_width > max_width:
            ratio = max_width / original_width
            new_width = max_width
            new_height = int(original_height * ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Compress image to JPEG format
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
        output_buffer.seek(0)
        
        # Encode back to base64
        compressed_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')
        
        # Return with data URI prefix
        return f"{header},{compressed_base64}"
    
    except Exception as e:
        raise ValueError(f"Failed to compress image: {str(e)}")


def get_image_size_kb(base64_string):
    """
    Calculate the size of a base64 encoded image in kilobytes.
    
    Args:
        base64_string (str): Base64 encoded image string
    
    Returns:
        float: Size in kilobytes
    """
    # Remove data URI prefix if present
    if ',' in base64_string:
        _, base64_data = base64_string.split(',', 1)
    else:
        base64_data = base64_string
    
    # Calculate size in KB
    size_bytes = len(base64_data) * 3 / 4  # Base64 encoding increases size by ~33%
    return size_bytes / 1024
