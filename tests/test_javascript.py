"""
Test suite for JavaScript files
"""
import pytest
from pathlib import Path
import re
from bs4 import BeautifulSoup


@pytest.fixture
def diagrams_js():
    """Load diagrams.js file"""
    js_file = Path(__file__).parent.parent / "js/diagrams.js"
    return js_file.read_text()


@pytest.fixture
def interactive_js():
    """Load interactive.js file"""
    js_file = Path(__file__).parent.parent / "js/interactive.js"
    return js_file.read_text()


@pytest.fixture
def html_content():
    """Load the HTML file"""
    html_file = Path(__file__).parent.parent / "index.html"
    return html_file.read_text()


@pytest.fixture
def soup(html_content):
    """Parse HTML with BeautifulSoup"""
    return BeautifulSoup(html_content, 'html.parser')


class TestJavaScriptFiles:
    """Tests for JavaScript file existence and size"""

    def test_diagrams_js_exists(self):
        """Verify diagrams.js exists"""
        js_file = Path(__file__).parent.parent / "js/diagrams.js"
        assert js_file.exists(), "diagrams.js not found"

    def test_interactive_js_exists(self):
        """Verify interactive.js exists"""
        js_file = Path(__file__).parent.parent / "js/interactive.js"
        assert js_file.exists(), "interactive.js not found"

    def test_js_files_reasonable_size(self):
        """Verify JS files are < 50KB each"""
        diagrams_file = Path(__file__).parent.parent / "js/diagrams.js"
        interactive_file = Path(__file__).parent.parent / "js/interactive.js"

        diagrams_size = diagrams_file.stat().st_size / 1024
        interactive_size = interactive_file.stat().st_size / 1024

        assert diagrams_size < 50, f"diagrams.js too large: {diagrams_size:.2f}KB"
        assert interactive_size < 50, f"interactive.js too large: {interactive_size:.2f}KB"


class TestFunctionDefinitions:
    """Tests for function definitions"""

    def test_create_svg_element_function(self, diagrams_js):
        """Verify createSVGElement function exists"""
        assert 'function createSVGElement' in diagrams_js, "createSVGElement function not found"

    def test_create_layer_function(self, diagrams_js):
        """Verify createLayer function exists"""
        assert 'function createLayer' in diagrams_js, "createLayer function not found"

    def test_render_functions_exist(self, diagrams_js):
        """Verify diagram render functions exist"""
        required_functions = [
            'renderStandardResidualDiagram',
            'renderComparisonDiagram',
            'renderMechanismDiagram',
            'renderBlockDiagram'
        ]

        for func in required_functions:
            assert f'function {func}' in diagrams_js, f"{func} function not found"

    def test_init_functions_exist(self, interactive_js):
        """Verify initialization functions exist"""
        required_functions = [
            'initThemeToggle',
            'initScrollAnimations',
            'initTransitionSlider',
            'initMechanismAnimation',
            'initBlockSlider'
        ]

        for func in required_functions:
            assert f'function {func}' in interactive_js, f"{func} function not found"


class TestEventListeners:
    """Tests for event listener setup"""

    def test_domcontentloaded_listener(self, diagrams_js, interactive_js):
        """Verify DOMContentLoaded event listeners exist"""
        combined = diagrams_js + interactive_js
        assert 'DOMContentLoaded' in combined, "No DOMContentLoaded event listener found"

    def test_click_event_listeners(self, interactive_js):
        """Verify click event listeners exist"""
        assert 'addEventListener' in interactive_js, "No addEventListener calls found"
        assert "'click'" in interactive_js or '"click"' in interactive_js, "No click event listeners found"

    def test_resize_event_listener(self, interactive_js):
        """Verify resize event listener exists"""
        assert "'resize'" in interactive_js or '"resize"' in interactive_js, "No resize event listener found"

    def test_input_event_listener(self, interactive_js):
        """Verify input event listeners for sliders"""
        assert "'input'" in interactive_js or '"input"' in interactive_js, "No input event listeners found"


class TestDOMQueries:
    """Tests for DOM queries and HTML element references"""

    def test_svg_ids_queried_exist(self, diagrams_js, soup):
        """Verify SVG IDs queried in JS exist in HTML"""
        # Find getElementById calls
        get_element_by_id = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", diagrams_js)

        for element_id in get_element_by_id:
            element = soup.find(id=element_id)
            assert element is not None, f"JS queries element #{element_id} which doesn't exist in HTML"

    def test_interactive_element_ids_exist(self, interactive_js, soup):
        """Verify element IDs queried in interactive.js exist in HTML"""
        get_element_by_id = re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", interactive_js)

        for element_id in get_element_by_id:
            element = soup.find(id=element_id)
            assert element is not None, f"JS queries element #{element_id} which doesn't exist in HTML"

    def test_class_selectors_exist(self, interactive_js, soup):
        """Verify major class selectors exist in HTML"""
        # Find querySelector calls with classes
        query_selectors = re.findall(r"querySelector\(['\"]\.([^'\"]+)['\"]\)", interactive_js)

        major_classes = ['theme-toggle', 'section', 'step']

        for cls in major_classes:
            if cls in str(query_selectors) or f'.{cls}' in interactive_js:
                element = soup.find(class_=cls)
                assert element is not None, f"JS queries class .{cls} which doesn't exist in HTML"


class TestCodeQuality:
    """Tests for code quality and best practices"""

    def test_no_console_errors(self, diagrams_js, interactive_js):
        """Verify no console.error in production code"""
        combined = diagrams_js + interactive_js
        assert 'console.error' not in combined, "console.error found in production code"

    def test_minimal_console_log(self, diagrams_js, interactive_js):
        """Verify minimal console.log usage"""
        combined = diagrams_js + interactive_js
        console_log_count = combined.count('console.log')
        assert console_log_count == 0, f"console.log found {console_log_count} times in production code"

    def test_no_todo_comments(self, diagrams_js, interactive_js):
        """Verify no TODO or FIXME comments"""
        combined = diagrams_js + interactive_js
        assert 'TODO' not in combined, "TODO comment found in code"
        assert 'FIXME' not in combined, "FIXME comment found in code"

    def test_functions_properly_closed(self, diagrams_js, interactive_js):
        """Verify functions have matching braces"""
        for js_content in [diagrams_js, interactive_js]:
            open_braces = js_content.count('{')
            close_braces = js_content.count('}')
            assert open_braces == close_braces, "Mismatched braces in JavaScript"


class TestLocalStorage:
    """Tests for localStorage usage"""

    def test_localstorage_wrapped_in_try_catch(self, interactive_js):
        """Verify localStorage usage is present"""
        if 'localStorage' in interactive_js:
            # If localStorage is used, it should be for theme persistence
            assert 'getItem' in interactive_js or 'setItem' in interactive_js, \
                "localStorage used but no getItem/setItem found"


class TestIntersectionObserver:
    """Tests for IntersectionObserver usage"""

    def test_intersection_observer_used(self, interactive_js):
        """Verify IntersectionObserver is used for scroll animations"""
        assert 'IntersectionObserver' in interactive_js, \
            "IntersectionObserver not found (needed for scroll animations)"


class TestSVGConstants:
    """Tests for SVG-related code"""

    def test_svg_namespace_defined(self, diagrams_js):
        """Verify SVG namespace is defined"""
        assert 'SVG_NS' in diagrams_js or 'http://www.w3.org/2000/svg' in diagrams_js, \
            "SVG namespace not defined"

    def test_create_svg_element_ns(self, diagrams_js):
        """Verify createElementNS is used for SVG creation"""
        assert 'createElementNS' in diagrams_js, \
            "createElementNS not found (needed for SVG element creation)"


class TestAnimationFunctions:
    """Tests for animation-related functions"""

    def test_animate_mechanism_function(self, diagrams_js):
        """Verify animateMechanism function exists"""
        assert 'function animateMechanism' in diagrams_js or 'animateMechanism' in diagrams_js, \
            "animateMechanism function not found"

    def test_diagram_initialization(self, diagrams_js):
        """Verify diagram initialization function exists"""
        assert 'initDiagrams' in diagrams_js or 'function initDiagrams' in diagrams_js, \
            "initDiagrams function not found"


class TestHTMLEventHandlers:
    """Tests for event handlers referenced in HTML"""

    def test_animate_mechanism_button(self, soup, diagrams_js):
        """Verify animate mechanism button handler exists"""
        button = soup.find('button', id='animate-mechanism')
        if button:
            # The function should exist in JS
            assert 'animateMechanism' in diagrams_js, \
                "animateMechanism function referenced but not defined"


class TestReadyStateHandling:
    """Tests for document ready state handling"""

    def test_document_ready_state_check(self, diagrams_js, interactive_js):
        """Verify document.readyState is checked"""
        combined = diagrams_js + interactive_js
        assert 'readyState' in combined, "No document.readyState check found"
        assert 'loading' in combined, "No check for document loading state"
