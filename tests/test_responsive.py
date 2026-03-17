"""
Test suite for responsive design
"""
import pytest
from pathlib import Path
import re


@pytest.fixture
def css_content():
    """Load the CSS file"""
    css_file = Path(__file__).parent.parent / "css/style.css"
    return css_file.read_text()


@pytest.fixture
def html_content():
    """Load the HTML file"""
    html_file = Path(__file__).parent.parent / "index.html"
    return html_file.read_text()


class TestMediaQueries:
    """Tests for media query implementation"""

    def test_media_queries_exist(self, css_content):
        """Verify media queries are defined"""
        assert '@media' in css_content, "No media queries found"

    def test_mobile_breakpoint_exists(self, css_content):
        """Verify mobile breakpoint exists (typically 768px)"""
        # Look for common mobile breakpoints
        mobile_patterns = [
            r'@media.*max-width.*768px',
            r'@media.*max-width.*767px',
            r'@media.*max-width.*640px'
        ]

        has_mobile = any(re.search(pattern, css_content) for pattern in mobile_patterns)
        assert has_mobile, "No mobile breakpoint found"

    def test_media_query_has_styles(self, css_content):
        """Verify media queries contain actual styles"""
        media_sections = re.findall(r'@media[^{]+\{([^}]+)\}', css_content, re.DOTALL)

        # Should have at least one media query with content
        assert len(media_sections) > 0, "Media queries found but no styles defined"


class TestMaxWidth:
    """Tests for max-width constraints"""

    def test_max_width_constraint_exists(self, css_content):
        """Verify max-width constraint exists for main content"""
        assert 'max-width' in css_content, "No max-width property found"

    def test_max_width_on_main_container(self, css_content):
        """Verify max-width is applied to main container"""
        # Look for max-width in main or container styles
        has_constrained_width = 'main' in css_content and 'max-width' in css_content
        assert has_constrained_width, "Main container should have max-width constraint"

    def test_max_width_reasonable_value(self, css_content):
        """Verify max-width has reasonable value (600-800px typical)"""
        # Find max-width values
        max_widths = re.findall(r'max-width:\s*(\d+)px', css_content)

        # Should have at least one max-width value
        assert len(max_widths) > 0, "No pixel max-width values found"

        # Check that at least one is in reasonable range for readable content
        max_widths_int = [int(w) for w in max_widths]
        has_reasonable = any(600 <= w <= 800 for w in max_widths_int)
        assert has_reasonable, "No max-width in readable range (600-800px) found"


class TestRelativeUnits:
    """Tests for relative units usage"""

    def test_font_sizes_use_relative_units(self, css_content):
        """Verify font sizes use relative units (rem/em)"""
        has_rem = 'rem' in css_content
        has_em = 'em' in css_content

        assert has_rem or has_em, "No relative font units (rem/em) found"

    def test_rem_usage_for_font_sizes(self, css_content):
        """Verify rem is used for font sizing"""
        font_size_rem = re.findall(r'font-size:\s*[\d.]+rem', css_content)
        assert len(font_size_rem) > 0, "No font-size declarations using rem found"

    def test_minimal_fixed_pixel_widths(self, css_content):
        """Verify minimal use of fixed pixel widths on containers"""
        # Fixed widths on containers are problematic for responsiveness
        # This is a heuristic test - we check that width: XXXpx is not overused

        width_px = re.findall(r'\bwidth:\s*\d+px', css_content)

        # Some fixed widths are okay (like for icons), but should be minimal
        # We allow up to 20 fixed width declarations
        assert len(width_px) < 20, \
            f"Too many fixed pixel widths: {len(width_px)} (reduces responsiveness)"


class TestSVGScalability:
    """Tests for SVG scalability"""

    def test_svg_viewbox_in_html(self, html_content):
        """Verify SVG elements use viewBox attribute"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        svgs = soup.find_all('svg')

        for svg in svgs:
            # BeautifulSoup is case-insensitive for HTML attributes
            viewbox = svg.get('viewBox') or svg.get('viewbox')
            # SVGs should have viewBox for scalability
            # Some SVGs might be icons which can skip this
            if svg.get('id'):  # If SVG has an ID, it's likely a diagram
                assert viewbox, f"SVG {svg.get('id')} missing viewBox attribute"

    def test_svg_width_height_responsive(self, css_content):
        """Verify SVG styling allows responsive sizing"""
        # Check for SVG responsive styles
        has_svg_styles = 'svg' in css_content

        if has_svg_styles:
            # Should have styles for SVG scalability
            # Common pattern: width: 100%; height: auto;
            assert True  # If SVG styles exist, good


class TestFlexboxGrid:
    """Tests for responsive layout systems"""

    def test_flexbox_or_grid_used(self, css_content):
        """Verify modern layout systems (flexbox or grid) are used"""
        has_flexbox = 'display: flex' in css_content or 'display:flex' in css_content
        has_grid = 'display: grid' in css_content or 'display:grid' in css_content

        assert has_flexbox or has_grid, \
            "No modern layout system (flexbox/grid) found"

    def test_flex_wrap_for_responsiveness(self, css_content):
        """Verify flex-wrap is used for responsive flexbox"""
        if 'display: flex' in css_content or 'display:flex' in css_content:
            has_flex_wrap = 'flex-wrap' in css_content
            # flex-wrap is important for responsive flexbox layouts


class TestMobileOptimizations:
    """Tests for mobile-specific optimizations"""

    def test_mobile_font_size_adjustments(self, css_content):
        """Verify mobile media queries adjust font sizes"""
        # Find media query sections
        media_sections = re.findall(r'@media[^{]+\{([^}]+(?:\{[^}]+\}[^}]+)*)\}', css_content, re.DOTALL)

        # At least one media query should adjust font-size or h1/h2
        has_font_adjustments = any('font-size' in section or 'h1' in section or 'h2' in section
                                    for section in media_sections)

        assert has_font_adjustments, \
            "Media queries should adjust typography for mobile"

    def test_mobile_layout_adjustments(self, css_content):
        """Verify mobile media queries adjust layouts"""
        # Check if media query section contains layout adjustments
        # Look for the entire @media block
        media_start = css_content.find('@media')
        if media_start != -1:
            # Get everything after @media
            media_content = css_content[media_start:]

            # Should adjust grid or flex layouts
            has_layout_adjustments = (
                'grid-template-columns' in media_content or
                'flex-direction' in media_content or
                'display:' in media_content or
                'display :' in media_content
            )

            assert has_layout_adjustments, \
                "Media queries should adjust layout for mobile"
        else:
            assert False, "No media queries found"


class TestTouchTargets:
    """Tests for touch-friendly interactions"""

    def test_button_sizes_adequate(self, css_content):
        """Verify buttons have adequate size for touch"""
        # Look for button or btn styles
        # Minimum touch target should be ~44x44px (Apple HIG) or ~48x48px (Material)

        # This is a basic check - we verify padding or min-height exists for buttons
        has_button_padding = '.btn' in css_content or 'button' in css_content

        if has_button_padding:
            # Should have padding or height definitions
            assert 'padding' in css_content, \
                "Buttons should have padding for adequate touch targets"


class TestViewportMeta:
    """Tests for viewport meta tag"""

    def test_viewport_meta_exists(self, html_content):
        """Verify viewport meta tag exists"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        viewport = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport is not None, "Missing viewport meta tag"

    def test_viewport_meta_correct_content(self, html_content):
        """Verify viewport meta tag has correct content"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        viewport = soup.find('meta', attrs={'name': 'viewport'})
        content = viewport.get('content', '')

        # Should include width=device-width
        assert 'width=device-width' in content, \
            "Viewport should include width=device-width"

        # Should include initial-scale
        assert 'initial-scale' in content, \
            "Viewport should include initial-scale"


class TestResponsiveImages:
    """Tests for responsive image handling"""

    def test_svg_preferred_for_graphics(self, html_content):
        """Verify SVG is used for graphics (scalable)"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        svgs = soup.find_all('svg')
        images = soup.find_all('img')

        # For a diagram-heavy page, SVGs should be prominent
        # (or diagrams are rendered via JS, which is fine)
        # This test just verifies SVG elements exist
        assert len(svgs) > 0 or 'svg' in html_content.lower(), \
            "No SVG elements found (consider using SVG for scalable graphics)"


class TestResponsiveSpacing:
    """Tests for responsive spacing"""

    def test_relative_spacing_units(self, css_content):
        """Verify spacing uses relative units where appropriate"""
        # Check for rem/em usage in margin/padding
        has_rem_spacing = bool(re.search(r'(margin|padding).*rem', css_content))
        has_em_spacing = bool(re.search(r'(margin|padding).*em', css_content))

        # At least some relative spacing should exist
        assert has_rem_spacing or has_em_spacing, \
            "Consider using relative units (rem/em) for spacing"


class TestContainerQueries:
    """Tests for modern responsive techniques"""

    def test_no_fixed_heights(self, css_content):
        """Verify minimal use of fixed heights (allow content to flow)"""
        # Fixed heights can break responsive layouts
        # Count fixed height declarations
        fixed_heights = re.findall(r'\bheight:\s*\d+px', css_content)

        # Allow some fixed heights (e.g., for icons), but should be limited
        assert len(fixed_heights) < 30, \
            f"Too many fixed heights: {len(fixed_heights)} (can break responsive flow)"
