// ABOUTME: Re-exports the htmx hx-csp extension via @alltuner/vibetuner/htmx/csp and
// ABOUTME: enables safeEval, so hx-on:/hx-live stay CSP-safe without unsafe-eval.
import "./htmx-safeeval.js";
import "htmx.org/dist/ext/hx-csp.js";
