from __future__ import print_function
from matplotlib.testing.compare import compare_images
from matplotlib.testing.decorators import _image_directories
import os
import shutil

baseline_dir, result_dir = _image_directories(lambda: 'dummy func')

# Tests of the image comparison algorithm.
def image_comparison_expect_rms(im1, im2, tol, expect_rms):
    """Compare two images, expecting a particular RMS error.

    im1 and im2 are filenames relative to the baseline_dir directory.

    tol is the tolerance to pass to compare_images.

    expect_rms is the expected RMS value, or None. If None, the test will
    succeed if compare_images succeeds. Otherwise, the test will succeed if
    compare_images fails and returns an RMS error almost equal to this value.
    """
    from nose.tools import assert_almost_equal
    from nose.tools import assert_is_none, assert_is_not_none
    im1 = os.path.join(baseline_dir, im1)
    im2_src = os.path.join(baseline_dir, im2)
    im2 = os.path.join(result_dir, im2)
    # Move im2 from baseline_dir to result_dir. This will ensure that
    # compare_images writes the diff file to result_dir, instead of trying to
    # write to the (possibly read-only) baseline_dir.
    shutil.copyfile(im2_src, im2)
    results = compare_images(im1, im2, tol=tol, in_decorator=True)

    if expect_rms is None:
        assert_is_none(results)
    else:
        assert_is_not_none(results)
        assert_almost_equal(expect_rms, results['rms'], places=4)

def test_image_compare_basic():
    """Test comparison of an image and the same image with minor differences."""
    # This expects the images to compare equal under normal tolerance, and have
    # a small RMS.
    im1 = 'cosine_peak-nn-img.png'
    im2 = 'cosine_peak-nn-img-minorchange.png'
    image_comparison_expect_rms(im1, im2, tol=10, expect_rms=None)

    # Now test with no tolerance.
    image_comparison_expect_rms(im1, im2, tol=0, expect_rms=2.99949)

def test_image_compare_1px_offset():
    """Test comparison with an image that is shifted by 1px in the X axis."""
    im1 = 'cosine_peak-nn-img.png'
    im2 = 'cosine_peak-nn-img-1px-offset.png'
    image_comparison_expect_rms(im1, im2, tol=0, expect_rms=22.04263)

def test_image_compare_title_1px_offset():
    """Test comparison with an image with the title shifted by 1px in the X
    axis."""
    im1 = 'cosine_peak-nn-img.png'
    im2 = 'cosine_peak-nn-img-title-1px-offset.png'
    image_comparison_expect_rms(im1, im2, tol=0, expect_rms=13.77513)

def test_image_compare_scrambled():
    """Test comparison of an image and the same image scrambled."""
    # This expects the images to compare completely different, with a very large
    # RMS.
    # Note: The image has been scrambled in a specific way, by having each
    # colour component of each pixel randomly placed somewhere in the image. It
    # contains exactly the same number of pixels of each colour value of R, G
    # and B, but in a totally different position.
    im1 = 'cosine_peak-nn-img.png'
    im2 = 'cosine_peak-nn-img-scrambled.png'
    # Test with no tolerance to make sure that we pick up even a very small RMS
    # error.
    image_comparison_expect_rms(im1, im2, tol=0, expect_rms=153.19994)

def test_image_compare_shade_difference():
    """Test comparison of an image and a slightly brighter image."""
    # The two images are solid colour, with the second image being exactly 1
    # colour value brighter.
    # This expects the images to compare equal under normal tolerance, and have
    # an RMS of exactly 1.
    im1 = 'all127.png'
    im2 = 'all128.png'
    image_comparison_expect_rms(im1, im2, tol=0, expect_rms=1.0)

    # Now test the reverse comparison.
    image_comparison_expect_rms(im2, im1, tol=0, expect_rms=1.0)
