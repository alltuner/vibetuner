// ABOUTME: Turns on htmx safeEval before the hx-csp extension registers, so hx-csp
// ABOUTME: evaluates hx-on:/hx-live via nonce-based script injection, not new Function().
import htmx from "htmx.org";

// hx-csp reads htmx.config.safeEval synchronously in its init (which runs the
// moment the extension module evaluates), so this must be set first. Keeping it
// in its own module lets htmx-csp.js import it ahead of the extension regardless
// of how config.js orders the framework imports.
htmx.config.safeEval = true;
