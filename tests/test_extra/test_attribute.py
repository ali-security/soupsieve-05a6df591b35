"""Test attribute selectors."""
import signal
import time
import soupsieve as sv
from .. import util


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def assert_fails_fast(self, selector, timeout=3):
        """Assert that a malformed selector raises a syntax error quickly instead of hanging."""

        if hasattr(signal, 'SIGALRM'):
            def timeout_handler(signum, frame):
                """Interrupt a parse that takes too long."""

                raise TimeoutError

            original = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            passed = False
            try:
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile(selector)
                passed = True
            except TimeoutError:
                pass
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original)
            self.assertTrue(passed)
        else:
            # `SIGALRM` is not available (Windows), so time the parse on the wall clock instead.
            start = time.perf_counter()
            with self.assertRaises(sv.SelectorSyntaxError):
                sv.compile(selector)
            self.assertLess(time.perf_counter() - start, timeout)

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        self.assert_fails_fast('[a="' + ('x' * 300))

    def test_bad_attribute_unclused_single_quote(self):
        """Test bad attribute with an unclosed single quoted value fails for syntax error, not timeout error."""

        self.assert_fails_fast("[a='" + ('x' * 300))

    def test_bad_attribute_unclused_unquoted(self):
        """Test bad attribute with an unclosed unquoted value fails for syntax error, not timeout error."""

        self.assert_fails_fast('[a=' + ('x' * 300))

    def test_attribute_unquoted_value(self):
        """Test attribute with unquoted, identifier style values."""

        markup = """
        <div id="div">
        <p id="0" data-value="a-b">Some text</p>
        <p id="1" data-value="a5">Some text</p>
        <p id="2" data-value="--a">Some text</p>
        <p id="3" data-value="a_b">Some text</p>
        <p id="4" data-value="123">Some text</p>
        </div>
        """

        self.assert_selector(markup, '[data-value=a-b]', ["0"], flags=util.PYHTML)
        self.assert_selector(markup, '[data-value=a5]', ["1"], flags=util.PYHTML)
        self.assert_selector(markup, '[data-value=--a]', ["2"], flags=util.PYHTML)
        self.assert_selector(markup, '[data-value=a_b]', ["3"], flags=util.PYHTML)
        self.assert_selector(markup, '[data-value=\\31 23]', ["4"], flags=util.PYHTML)
