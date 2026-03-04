from unittest.mock import MagicMock
import sys
import io
from PIL import Image

# 1. Mock streamlit BEFORE importing the app code
mock_st = MagicMock()
# This covers st.secrets.get("...")
mock_st.secrets.get.return_value = "mock_token"
# This covers st.secrets["..."]
mock_st.secrets.__getitem__.return_value = "mock_token"

sys.modules["streamlit"] = mock_st

# 2. Now import your function
from streamlit_app import compress_image

def test_compress_image_rgba_conversion():
    """Verify RGBA images are converted to RGB during compression."""
    # Create a small RGBA image (red with 50% transparency)
    rgba_image = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    img_byte_arr = io.BytesIO()
    rgba_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Run the compression
    compressed_data = compress_image(img_byte_arr)
    
    # Check the result is valid JPEG (which must be RGB)
    result_img = Image.open(io.BytesIO(compressed_data))
    assert result_img.mode == "RGB"
    assert result_img.format == "JPEG"