# Released under the MIT License. See LICENSE for details.
#
"""Appearance functionality for sillies."""
from __future__ import annotations

import bascenev1 as bs


def get_appearances(include_locked: bool = False) -> list[str]:
    """Get the list of available silly appearances."""
    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    plus = bs.app.plus
    assert plus is not None

    assert bs.app.classic is not None
    return [
        s
        for s in list(bs.app.classic.silly_appearances.keys())
    ]


class Appearance:
    """Create and fill out one of these suckers to define a silly appearance."""

    def __init__(self, name: str):
        assert bs.app.classic is not None
        self.name = name
        if self.name in bs.app.classic.silly_appearances:
            raise RuntimeError(
                f'silly appearance name "{self.name}" already exists.'
            )
        bs.app.classic.silly_appearances[self.name] = self
        self.color_texture = ''
        self.color_mask_texture = ''
        self.icon_texture = ''
        self.icon_mask_texture = ''
        self.head_mesh = ''
        self.torso_mesh = ''
        self.pelvis_mesh = ''
        self.upper_arm_mesh = ''
        self.forearm_mesh = ''
        self.hand_mesh = ''
        self.upper_leg_mesh = ''
        self.lower_leg_mesh = ''
        self.toes_mesh = ''
        self.jump_sounds: list[str] = []
        self.attack_sounds: list[str] = []
        self.impact_sounds: list[str] = []
        self.death_sounds: list[str] = []
        self.pickup_sounds: list[str] = []
        self.fall_sounds: list[str] = []
        self.style = 'spaz'
        self.default_color: tuple[float, float, float] | None = None
        self.default_highlight: tuple[float, float, float] | None = None


def register_appearances() -> None:
    """Register our builtin silly appearances."""

    # This is quite ugly but will be going away so not worth cleaning up.
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements

    # SoK #######################################
    t = Appearance('Sucuk')
    t.color_texture = 'neoSpazColor'
    t.color_mask_texture = 'neoSpazColorMask'
    t.icon_texture = 'neoSpazIcon'
    t.icon_mask_texture = 'neoSpazIconColorMask'
    t.head_mesh = 'neoSpazHead'
    t.torso_mesh = 'neoSpazTorso'
    t.pelvis_mesh = 'neoSpazPelvis'
    t.upper_arm_mesh = 'neoSpazUpperArm'
    t.forearm_mesh = 'neoSpazForeArm'
    t.hand_mesh = 'neoSpazHand'
    t.upper_leg_mesh = 'neoSpazUpperLeg'
    t.lower_leg_mesh = 'neoSpazLowerLeg'
    t.toes_mesh = 'neoSpazToes'
    sounds = ['blank']
    t.death_sounds = ['blank']
    t.pickup_sounds = sounds
    t.fall_sounds = ['blank']
    t.style = 'spaz'