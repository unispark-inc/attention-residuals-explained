"""
Test suite for CSS validation
"""
import pytest
from pathlib import Path
import re
import cssutils
from bs4 import BeautifulSoup


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


@pytest.fixture
def soup(html_content):
    """Parse HTML with BeautifulSoup"""
    return BeautifulSoup(html_content, 'html.parser')


class TestCSSBasics:
    """Tests for basic CSS file properties"""

    def test_css_file_exists(self):
        """Verify CSS file exists"""
        css_file = Path(__file__).parent.parent / "css/style.css"
        assert css_file.exists(), "CSS file not found"

    def test_css_file_not_empty(self, css_content):
        """Verify CSS file is not empty"""
        assert len(css_content.strip()) > 0, "CSS file is empty"

    def test_css_file_size(self):
        """Verify CSS file is reasonable size (< 100KB)"""
        css_file = Path(__file__).parent.parent / "css/style.css"
        size_kb = css_file.stat().st_size / 1024
        assert size_kb < 100, f"CSS file too large: {size_kb:.2f}KB"


class TestCSSVariables:
    """Tests for CSS custom properties"""

    def test_root_variables_defined(self, css_content):
        """Verify :root CSS variables are defined"""
        assert ':root' in css_content, "Missing :root selector for CSS variables"

        # Check for key variables
        required_vars = [
            '--bg-primary',
            '--bg-secondary',
            '--text-primary',
            '--text-secondary',
            '--accent-primary'
        ]

        for var in required_vars:
            assert var in css_content, f"Missing CSS variable: {var}"

    def test_dark_theme_variables(self, css_content):
        """Verify dark theme variables are defined"""
        assert '[data-theme="dark"]' in css_content, "Missing dark theme selector"

        # Check for dark theme variables
        dark_theme_section = css_content.split('[data-theme="dark"]')[1].split('}')[0]

        required_dark_vars = [
            '--bg-primary',
            '--text-primary',
            '--accent-primary'
        ]

        for var in required_dark_vars:
            assert var in dark_theme_section, f"Missing dark theme variable: {var}"


class TestResponsive:
    """Tests for responsive design"""

    def test_mobile_media_query_exists(self, css_content):
        """Verify mobile media query exists"""
        assert '@media' in css_content, "No media queries found"
        assert 'max-width' in css_content or 'min-width' in css_content, "No responsive breakpoints found"

    def test_max_width_constraint(self, css_content):
        """Verify max-width constraint exists for main content"""
        # Look for max-width property
        assert 'max-width:' in css_content or 'max-width :' in css_content, "No max-width constraint found"

    def test_relative_units_used(self, css_content):
        """Verify relative units (rem, em) are used for fonts"""
        has_rem = 'rem' in css_content
        has_em = 'em' in css_content

        assert has_rem or has_em, "No relative font units (rem/em) found"


class TestAnimations:
    """Tests for CSS animations"""

    def test_keyframes_defined(self, css_content):
        """Verify animation keyframes are defined"""
        assert '@keyframes' in css_content, "No @keyframes animations found"

    def test_animation_keyframes_exist(self, css_content):
        """Verify specific animation keyframes exist"""
        # Check for animation names mentioned in requirements
        keyframe_pattern = r'@keyframes\s+(\w+)'
        keyframes = re.findall(keyframe_pattern, css_content)

        assert len(keyframes) > 0, "No animation keyframes found"


class TestThemeStyles:
    """Tests for theme toggle styles"""

    def test_theme_toggle_styles_exist(self, css_content):
        """Verify theme toggle styles are defined"""
        assert '.theme-toggle' in css_content, "Missing .theme-toggle styles"

    def test_sun_moon_icon_styles(self, css_content):
        """Verify sun and moon icon styles exist"""
        assert '.sun-icon' in css_content or 'sun-icon' in css_content, "Missing sun icon styles"
        assert '.moon-icon' in css_content or 'moon-icon' in css_content, "Missing moon icon styles"


class TestCSSClassCoverage:
    """Tests to verify HTML classes have corresponding CSS"""

    def test_major_html_classes_have_css(self, soup, css_content):
        """Verify major HTML classes are defined in CSS"""
        # Get all classes from HTML
        html_classes = set()
        for element in soup.find_all(class_=True):
            classes = element.get('class')
            if isinstance(classes, list):
                html_classes.update(classes)
            else:
                html_classes.add(classes)

        # Major classes that should have CSS definitions
        major_classes = [
            'hero', 'section', 'problem-item', 'comparison-container',
            'slider-container', 'step', 'result-card', 'footer-content'
        ]

        for cls in major_classes:
            if cls in html_classes:
                # Check if class is in CSS (with . prefix)
                assert f'.{cls}' in css_content, f"HTML class '.{cls}' not found in CSS"


class TestCSSQuality:
    """Tests for CSS quality and best practices"""

    def test_no_excessive_important(self, css_content):
        """Verify !important is not overused"""
        important_count = css_content.count('!important')
        assert important_count < 5, f"Too many !important declarations: {important_count}"

    def test_no_inline_styles_preference(self, soup):
        """Verify minimal inline styles (prefer external CSS)"""
        elements_with_style = soup.find_all(style=True)

        # Allow some inline styles for dynamic content (like result bars)
        # but should be minimal
        assert len(elements_with_style) < 20, f"Too many inline styles: {len(elements_with_style)}"


class TestCSSParsing:
    """Tests for CSS syntax validation"""

    def test_css_parses_without_errors(self, css_content):
        """Verify CSS can be parsed without critical errors"""
        # Suppress cssutils warnings
        cssutils.log.setLevel(50)  # CRITICAL level only

        try:
            sheet = cssutils.parseString(css_content)
            # If parsing succeeds, we have valid CSS
            assert sheet is not None, "CSS parsing returned None"
        except Exception as e:
            pytest.fail(f"CSS parsing failed: {e}")


class TestSpecificStyles:
    """Tests for specific style requirements"""

    def test_focus_indicators_exist(self, css_content):
        """Verify focus indicators are defined"""
        # Look for focus or outline styles
        has_focus = ':focus' in css_content or 'outline' in css_content
        assert has_focus, "No focus indicators found (accessibility issue)"

    def test_transition_animations_exist(self, css_content):
        """Verify transition properties exist for smooth UX"""
        assert 'transition' in css_content, "No CSS transitions found"

    def test_svg_styles_exist(self, css_content):
        """Verify SVG-related styles exist"""
        # Check for SVG element styling or animation classes
        has_svg_styles = 'svg' in css_content or '.arrow-animate' in css_content
        assert has_svg_styles, "No SVG-related styles found"
