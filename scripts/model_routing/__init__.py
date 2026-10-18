"""Generic model routing for coding-delegation.

Tool order comes from the user's prefs. The tier catalog is opt-in for frontier.
"""

from model_routing.choose import choose
from model_routing.fallback import plan_fallback
from model_routing.prejob import prejob

__all__ = ["choose", "plan_fallback", "prejob"]
