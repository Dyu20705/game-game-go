"""Pygame view package for Color Wars.

This package provides scene rendering and UI components.
It is organized as follows:

- Constants, layout, window: shared across all scenes
- gameplay_scene/: main game board rendering
- home_scene/, *_scene/: menu screens
- commons/: reusable UI components (Button, Panel, etc.)
- base/: abstract base classes for scenes
"""

# ============================================================================
# Shared view layer (constants, layout, window)
# ============================================================================
from .constants import *
from .layout import compute_layout, get_cell_from_mouse
from .window import drawScreen, toggle_fullscreen

# ============================================================================
# Gameplay scene (board rendering)
# ============================================================================
from .gameplay_scene import (
    drawBoard,
    drawDot,
    drawExplosionOverlay,
    drawHud,
    drawNode,
    drawScene,
    draw_gameplay_scene,
    get_control_lines,
    get_status_lines,
)

# ============================================================================
# Menu scenes
# ============================================================================
from .choose_diff_scene import draw_choose_diff_scene
from .choose_gamemode_scene import draw_choose_gamemode_scene
from .home_scene import compute_menu_icon_rects, difficulty_from_percent, draw_home_scene, run_home_menu
from .setting_scene import draw_setting_scene, draw_settings_icon
from .tutorial_scene import draw_tutorial_icon, draw_tutorial_scene
from .win_scene import draw_win_scene, get_win_action_rects

# ============================================================================
# UI components and base classes
# ============================================================================
from .commons.ui_components import Button, Panel, TextLabel
from .base.scene import BaseScene, SceneController

