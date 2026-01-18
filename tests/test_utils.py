import pytest
import base64
import io
from PIL import Image
from utils import compress_base64_image, get_image_size_kb


def create_test_image_base64(width=800, height=600, color=(255, 0, 0), format='JPEG'):
    """
    Helper function to create a test image in base64 format.
    
    Args:
        width (int): Image width in pixels
        height (int): Image height in pixels
        color (tuple): RGB color tuple
        format (str): Image format (JPEG or PNG)
    
    Returns:
        str: Base64 encoded image with data URI prefix
    """
    # Create a test image
    image = Image.new('RGB', (width, height), color)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    # Add data URI prefix
    mime_type = 'image/jpeg' if format == 'JPEG' else 'image/png'
    return f"data:{mime_type};base64,{img_base64}"


class TestCompressBase64Image:
    """Test suite for compress_base64_image function"""
    
    def test_compress_image_reduces_size(self):
        """Test that compression reduces image size"""
        # Create a large test image
        original_image = create_test_image_base64(width=1920, height=1080)
        original_size = get_image_size_kb(original_image)
        
        # Compress the image
        compressed_image = compress_base64_image(original_image, max_width=400, quality=85)
        compressed_size = get_image_size_kb(compressed_image)
        
        # Assert compressed size is smaller
        assert compressed_size < original_size, \
            f"Compressed size ({compressed_size:.2f}KB) should be smaller than original ({original_size:.2f}KB)"
        
        # Assert significant compression (at least 50% reduction)
        compression_ratio = compressed_size / original_size
        assert compression_ratio < 0.5, \
            f"Compression ratio ({compression_ratio:.2%}) should be less than 50%"
    
    def test_compress_image_maintains_aspect_ratio(self):
        """Test that compression maintains aspect ratio"""
        # Create a test image with specific aspect ratio (16:9)
        original_image = create_test_image_base64(width=1600, height=900)
        
        # Compress the image
        compressed_image = compress_base64_image(original_image, max_width=400)
        
        # Decode and check dimensions
        _, base64_data = compressed_image.split(',', 1)
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        width, height = image.size
        aspect_ratio = width / height
        
        # Original aspect ratio is 16:9 ≈ 1.778
        assert abs(aspect_ratio - 1.778) < 0.01, \
            f"Aspect ratio ({aspect_ratio:.3f}) should be approximately 1.778"
        
        # Width should be max_width or less
        assert width <= 400, f"Width ({width}) should be <= 400"
    
    def test_compress_small_image_no_resize(self):
        """Test that small images are not resized, only compressed"""
        # Create a small image (smaller than max_width)
        original_image = create_test_image_base64(width=300, height=200)
        
        # Compress the image
        compressed_image = compress_base64_image(original_image, max_width=400)
        
        # Decode and check dimensions
        _, base64_data = compressed_image.split(',', 1)
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        width, height = image.size
        
        # Dimensions should remain the same
        assert width == 300, f"Width should remain 300, got {width}"
        assert height == 200, f"Height should remain 200, got {height}"
    
    def test_compress_image_returns_valid_base64(self):
        """Test that compressed image is valid base64 with data URI"""
        original_image = create_test_image_base64(width=800, height=600)
        
        # Compress the image
        compressed_image = compress_base64_image(original_image)
        
        # Check format
        assert compressed_image.startswith('data:image/'), \
            "Compressed image should start with data URI prefix"
        assert ',base64,' in compressed_image or ';base64,' in compressed_image, \
            "Compressed image should contain base64 indicator"
        
        # Try to decode - should not raise exception
        _, base64_data = compressed_image.split(',', 1)
        try:
            decoded = base64.b64decode(base64_data)
            assert len(decoded) > 0, "Decoded data should not be empty"
        except Exception as e:
            pytest.fail(f"Failed to decode base64: {e}")
    
    def test_compress_image_without_data_uri_prefix(self):
        """Test compression works with base64 string without data URI prefix"""
        # Create image and remove data URI prefix
        original_image = create_test_image_base64(width=800, height=600)
        _, base64_only = original_image.split(',', 1)
        
        # Compress the image (without prefix)
        compressed_image = compress_base64_image(base64_only)
        
        # Should still return valid data URI
        assert compressed_image.startswith('data:image/'), \
            "Should add data URI prefix if not present"
    
    def test_compress_png_to_jpeg(self):
        """Test that PNG images are converted to JPEG"""
        # Create a PNG image
        original_image = create_test_image_base64(width=800, height=600, format='PNG')
        
        # Compress the image
        compressed_image = compress_base64_image(original_image)
        
        # Check that result is JPEG
        assert 'image/jpeg' in compressed_image, \
            "Compressed image should be JPEG format"
    
    def test_compress_rgba_image(self):
        """Test that RGBA images are properly converted"""
        # Create an RGBA image
        image = Image.new('RGBA', (800, 600), (255, 0, 0, 128))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        original_image = f"data:image/png;base64,{img_base64}"
        
        # Compress the image - should not raise exception
        try:
            compressed_image = compress_base64_image(original_image)
            assert compressed_image is not None
            assert 'image/jpeg' in compressed_image
        except Exception as e:
            pytest.fail(f"Failed to compress RGBA image: {e}")
    
    def test_compress_with_custom_quality(self):
        """Test compression with different quality settings"""
        original_image = create_test_image_base64(width=800, height=600)
        
        # Compress with high quality
        high_quality = compress_base64_image(original_image, max_width=400, quality=95)
        high_quality_size = get_image_size_kb(high_quality)
        
        # Compress with low quality
        low_quality = compress_base64_image(original_image, max_width=400, quality=50)
        low_quality_size = get_image_size_kb(low_quality)
        
        # Lower quality should result in smaller size
        assert low_quality_size < high_quality_size, \
            f"Low quality ({low_quality_size:.2f}KB) should be smaller than high quality ({high_quality_size:.2f}KB)"
    
    def test_compress_invalid_base64_raises_error(self):
        """Test that invalid base64 raises ValueError"""
        invalid_base64 = "data:image/jpeg;base64,INVALID_BASE64_STRING!!!"
        
        with pytest.raises(ValueError) as exc_info:
            compress_base64_image(invalid_base64)
        
        assert "Failed to compress image" in str(exc_info.value)


class TestGetImageSizeKB:
    """Test suite for get_image_size_kb function"""
    
    def test_get_size_with_data_uri(self):
        """Test getting size of image with data URI prefix"""
        test_image = create_test_image_base64(width=800, height=600)
        size = get_image_size_kb(test_image)
        
        assert size > 0, "Size should be greater than 0"
        assert isinstance(size, float), "Size should be a float"
    
    def test_get_size_without_data_uri(self):
        """Test getting size of image without data URI prefix"""
        test_image = create_test_image_base64(width=800, height=600)
        _, base64_only = test_image.split(',', 1)
        
        size = get_image_size_kb(base64_only)
        
        assert size > 0, "Size should be greater than 0"
    
    def test_larger_image_has_larger_size(self):
        """Test that larger images have larger file sizes"""
        small_image = create_test_image_base64(width=400, height=300)
        large_image = create_test_image_base64(width=1600, height=1200)
        
        small_size = get_image_size_kb(small_image)
        large_size = get_image_size_kb(large_image)
        
        assert large_size > small_size, \
            f"Large image ({large_size:.2f}KB) should be bigger than small image ({small_size:.2f}KB)"


class TestIntegration:
    """Integration tests for image compression workflow"""
    
    def test_compression_workflow(self):
        """Test complete compression workflow"""
        # Step 1: Create a large image (simulating camera capture)
        original_image = create_test_image_base64(width=1920, height=1080)
        original_size = get_image_size_kb(original_image)
        
        print(f"\n📊 Original image: {original_size:.2f}KB")
        
        # Step 2: Compress for database storage
        compressed_image = compress_base64_image(original_image, max_width=400, quality=85)
        compressed_size = get_image_size_kb(compressed_image)
        
        print(f"📊 Compressed image: {compressed_size:.2f}KB")
        print(f"📊 Compression ratio: {(compressed_size/original_size)*100:.1f}%")
        print(f"📊 Space saved: {original_size - compressed_size:.2f}KB")
        
        # Step 3: Verify compressed image is valid
        _, base64_data = compressed_image.split(',', 1)
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Assertions
        assert compressed_size < original_size
        assert image.format == 'JPEG'
        assert image.size[0] <= 400  # Width should be <= max_width
        assert compressed_size < 100, "Compressed image should be less than 100KB for typical use"
