# Released under the MIT License. See LICENSE for details.
#
"""Provides a window to display game credits."""

from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING

import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Sequence


class CreditsListWindow(bui.Window):
    """Window for displaying game credits."""

    def __init__(self, origin_widget: bui.Widget | None = None):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        import json

        bui.set_analytics_screen('Credits Window')

        # if they provided an origin-widget, scale up from that
        scale_origin: tuple[float, float] | None
        self._transition_out = 'out_right'
        transition = 'in_right'

        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale
        width = 870 if uiscale is bui.UIScale.SMALL else 670
        x_inset = 100 if uiscale is bui.UIScale.SMALL else 0
        height = 398 if uiscale is bui.UIScale.SMALL else 500

        self._r = 'creditsWindow'
        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height),
                transition=transition,
                toolbar_visibility='menu_minimal',
                scale=(
                    2.0
                    if uiscale is bui.UIScale.SMALL
                    else 1.3
                    if uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
                stack_offset=(0, -8)
                if uiscale is bui.UIScale.SMALL
                else (0, 0),
            )
        )

        if bui.app.ui_v1.use_toolbars and uiscale is bui.UIScale.SMALL:
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self._back
            )
        else:
            btn = bui.buttonwidget(
                parent=self._root_widget,
                position=(
                    40 + x_inset,
                    height - (68 if uiscale is bui.UIScale.SMALL else 62),
                ),
                size=(140, 60),
                scale=0.8,
                label=bui.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._back,
                autoselect=True,
            )
            bui.containerwidget(edit=self._root_widget, cancel_button=btn)

            bui.buttonwidget(
                edit=btn,
                button_type='backSmall',
                position=(
                    40 + x_inset,
                    height - (68 if uiscale is bui.UIScale.SMALL else 62) + 5,
                ),
                size=(60, 48),
                label=bui.charstr(bui.SpecialChar.BACK),
            )

        bui.textwidget(
            parent=self._root_widget,
            position=(0, height - (59 if uiscale is bui.UIScale.SMALL else 54)),
            size=(width, 30),
            text=bui.Lstr(
                resource=self._r + '.titleText',
                subs=[('${APP_NAME}', bui.Lstr(resource='titleText'))],
            ),
            h_align='center',
            color=bui.app.ui_v1.title_color,
            maxwidth=330,
            v_align='center',
        )

        scroll = bui.scrollwidget(
            parent=self._root_widget,
            position=(40 + x_inset, 35),
            size=(width - (80 + 2 * x_inset), height - 100),
            capture_arrows=True,
        )

        if bui.app.ui_v1.use_toolbars:
            bui.widget(
                edit=scroll,
                right_widget=bui.get_special_widget('party_button'),
            )
            if uiscale is bui.UIScale.SMALL:
                bui.widget(
                    edit=scroll,
                    left_widget=bui.get_special_widget('back_button'),
                )

        def _format_names(names2: Sequence[str], inset: float) -> str:
            sval = ''
            # measure a series since there's overlaps and stuff..
            space_width = (
                bui.get_string_width(' ' * 10, suppress_warning=True) / 10.0
            )
            spacing = 330.0
            col1 = inset
            col2 = col1 + spacing
            col3 = col2 + spacing
            line_width = 0.0
            nline = ''
            for name in names2:
                # move to the next column (or row) and print
                if line_width > col3:
                    sval += nline + '\n'
                    nline = ''
                    line_width = 0

                if line_width > col2:
                    target = col3
                elif line_width > col1:
                    target = col2
                else:
                    target = col1
                spacingstr = ' ' * int((target - line_width) / space_width)
                nline += spacingstr
                nline += name
                line_width = bui.get_string_width(nline, suppress_warning=True)
            if nline != '':
                sval += nline + '\n'
            return sval

        sound_and_music = bui.Lstr(
            resource=self._r + '.songCreditText'
        ).evaluate()
        sound_and_music = sound_and_music.replace(
            '${TITLE}', "'William Tell (Trumpet Entry)'"
        )
        sound_and_music = sound_and_music.replace(
            '${PERFORMER}', 'The Apollo Symphony Orchestra'
        )
        sound_and_music = sound_and_music.replace(
            '${PERFORMER}', 'The Apollo Symphony Orchestra'
        )
        sound_and_music = sound_and_music.replace(
            '${COMPOSER}', 'Gioacchino Rossini'
        )
        sound_and_music = sound_and_music.replace('${ARRANGER}', 'Chris Worth')
        sound_and_music = sound_and_music.replace('${PUBLISHER}', 'BMI')
        sound_and_music = sound_and_music.replace(
            '${SOURCE}', 'www.AudioSparx.com'
        )
        spc = '     '
        sound_and_music = spc + sound_and_music.replace('\n', '\n' + spc)
        names = [
            'HubOfTheUniverseProd',
            'Jovica',
            'LG',
            'Leady',
            'Percy Duke',
            'PhreaKsAccount',
            'Pogotron',
            'Rock Savage',
            'anamorphosis',
            'benboncan',
            'cdrk',
            'chipfork',
            'guitarguy1985',
            'jascha',
            'joedeshon',
            'loofa',
            'm_O_m',
            'mich3d',
            'sandyrb',
            'shakaharu',
            'sirplus',
            'stickman',
            'thanvannispen',
            'virotic',
            'zimbot',
        ]
        names.sort(key=lambda x: x.lower())
        freesound_names = _format_names(names, 90)

        # Need to bake this out and chop it up since we're passing our
        # 65535 vertex limit for meshes..
        # We can remove that limit once we drop support for GL ES2.. :-/
        # (or add mesh splitting under the hood)

        # What does the comment above me mean lmao
        txt = ('Square Hair Team:\n'
               'SoK - Lead Manager, Lead Developer\n'
               'Temp - Second Developer\n'
               'TheMikirog - Third Developer\n'
               'Nęo - Fourth Developer\n'
               '\n'
               'Special Credits:\n'
               'Artninja - Punch Sound Effects')
        lines = txt.splitlines()
        line_height = 20

        scale = 0.7
        self._sub_width = width - 80
        self._sub_height = line_height * len(lines) + 40

        container = self._subcontainer = bui.containerwidget(
            parent=scroll,
            size=(self._sub_width, self._sub_height),
            background=False,
            claims_left_right=False,
            claims_tab=False,
        )

        voffs = 0
        for line in lines:
            bui.textwidget(
                parent=container,
                padding=4,
                color=(0.7, 0.9, 0.7, 1.0),
                scale=scale,
                flatness=1.0,
                size=(0, 0),
                position=(0, self._sub_height - 20 + voffs),
                h_align='left',
                v_align='top',
                text=bui.Lstr(value=line),
            )
            voffs -= line_height

    def _back(self) -> None:
        from bauiv1lib.mainmenu import MainMenuWindow

        bui.containerwidget(
            edit=self._root_widget, transition=self._transition_out
        )
        assert bui.app.classic is not None
        bui.app.ui_v1.set_main_menu_window(
            MainMenuWindow(transition='in_left').get_root_widget(),
            from_window=self._root_widget,
        )
