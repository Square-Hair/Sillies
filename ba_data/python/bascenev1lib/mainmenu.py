# Released under the MIT License. See LICENSE for details.
#
"""Session and Activity for displaying the main menu bg."""
# pylint: disable=too-many-lines

from __future__ import annotations

import time
import random
import weakref
from typing import TYPE_CHECKING, override

import bascenev1 as bs
import bauiv1 as bui
from sillies import debug

if TYPE_CHECKING:
    from typing import Any


class MainMenuActivity(bs.Activity[bs.Player, bs.Team]):
    """Activity showing the rotating main menu bg stuff."""

    _stdassets = bs.Dependency(bs.AssetPackage, 'stdassets@1')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._logo_node: bs.Node | None = None
        self._custom_logo_tex_name: str | None = None
        self._word_actors: list[bs.Actor] = []
        self.my_name: bs.NodeActor | None = None
        self._host_is_navigating_text: bs.NodeActor | None = None
        self.version: bs.NodeActor | None = None
        self.bottom: bs.NodeActor | None = None
        self.vr_bottom_fill: bs.NodeActor | None = None
        self.vr_top_fill: bs.NodeActor | None = None
        self.terrain: bs.NodeActor | None = None
        self.trees: bs.NodeActor | None = None
        self.bgterrain: bs.NodeActor | None = None
        self._ts = 0.86
        self._language: str | None = None
        self._update_timer: bs.Timer | None = None
        self._attract_mode_timer: bs.Timer | None = None
        self._logo_sound = bs.getsound('menuLogoHit')

    @override
    def on_transition_in(self) -> None:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        super().on_transition_in()
        random.seed(123)
        app = bs.app
        env = app.env
        assert app.classic is not None

        plus = bui.app.plus
        assert plus is not None

        # FIXME: We shouldn't be doing things conditionally based on whether
        #  the host is VR mode or not (clients may differ in that regard).
        #  Any differences need to happen at the engine level so everyone
        #  sees things in their own optimal way.
        vr_mode = bs.app.env.vr

        if not bs.app.ui_v1.use_toolbars:
            color = (1.0, 1.0, 1.0, 1.0) if vr_mode else (0.5, 0.6, 0.5, 0.6)

            # FIXME: Need a node attr for vr-specific-scale.
            scale = (
                0.9
                if (app.ui_v1.uiscale is bs.UIScale.SMALL or vr_mode)
                else 0.7
            )
            self.my_name = bs.NodeActor(
                bs.newnode(
                    'text',
                    attrs={
                        'v_attach': 'bottom',
                        'h_align': 'center',
                        'color': color,
                        'flatness': 1.0,
                        'shadow': 1.0 if vr_mode else 0.5,
                        'scale': scale,
                        'position': (0, 10),
                        'vr_depth': -10,
                        'text': '\xa9 2024 Square Hair Team',
                    },
                )
            )

        # Throw up some text that only clients can see so they know that the
        # host is navigating menus while they're just staring at an
        # empty-ish screen.
        tval = bs.Lstr(
            resource='hostIsNavigatingMenusText',
            subs=[('${HOST}', plus.get_v1_account_display_string())],
        )
        self._host_is_navigating_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'text': tval,
                    'client_only': True,
                    'position': (0, -200),
                    'flatness': 1.0,
                    'h_align': 'center',
                },
            )
        )
        if not app.classic.main_menu_did_initial_transition and hasattr(
            self, 'my_name'
        ):
            assert self.my_name is not None
            assert self.my_name.node
            bs.animate(self.my_name.node, 'opacity', {2.3: 0, 3.0: 1.0})

        # FIXME: We shouldn't be doing things conditionally based on whether
        #  the host is vr mode or not (clients may not be or vice versa).
        #  Any differences need to happen at the engine level so everyone sees
        #  things in their own optimal way.
        vr_mode = app.env.vr
        uiscale = app.ui_v1.uiscale

        # In cases where we're doing lots of dev work lets always show the
        # build number.
        force_show_build_number = False

        if not bs.app.ui_v1.use_toolbars:
            if env.debug or env.test or force_show_build_number:
                if env.debug:
                    text = bs.Lstr(
                        value='${V} (${B}) (${D})',
                        subs=[
                            ('${V}', app.env.engine_version),
                            ('${B}', str(app.env.engine_build_number)),
                            ('${D}', bs.Lstr(resource='debugText')),
                        ],
                    )
                else:
                    text = bs.Lstr(
                        value='${V} (${B})',
                        subs=[
                            ('${V}', app.env.engine_version),
                            ('${B}', str(app.env.engine_build_number)),
                        ],
                    )
            else:
                text = bs.Lstr(
                    value='${V}', subs=[('${V}', app.env.engine_version)]
                )
            scale = 0.9 if (uiscale is bs.UIScale.SMALL or vr_mode) else 0.7
            color = (1, 1, 1, 1) if vr_mode else (0.5, 0.6, 0.5, 0.7)
            self.version = bs.NodeActor(
                bs.newnode(
                    'text',
                    attrs={
                        'v_attach': 'bottom',
                        'h_attach': 'right',
                        'h_align': 'right',
                        'flatness': 1.0,
                        'vr_depth': -10,
                        'shadow': 1.0 if vr_mode else 0.5,
                        'color': color,
                        'scale': scale,
                        'position': (-260, 10) if vr_mode else (-10, 10),
                        'text': text,
                    },
                )
            )
            if not app.classic.main_menu_did_initial_transition:
                assert self.version.node
                bs.animate(self.version.node, 'opacity', {2.3: 0, 3.0: 1.0})

        trees_mesh = bs.getmesh('trees')
        trees_texture = bs.gettexture('treesColor')
        bgtex = bs.gettexture('menuBG')
        bgmesh = bs.getmesh('thePadBG')

        # Load these last since most platforms don't use them.
        vr_bottom_fill_mesh = bs.getmesh('thePadVRFillBottom')
        vr_top_fill_mesh = bs.getmesh('thePadVRFillTop')

        gnode = self.globalsnode

        tint = (0.765, 0.506, 0.788)
        gnode.tint = tint
        gnode.ambient_color = (0.765, 0.506, 0.788)
        gnode.vignette_outer = (0.45, 0.55, 0.54)
        gnode.vignette_inner = (0.99, 0.98, 0.98)

        self.vr_top_fill = bs.NodeActor(
            bs.newnode(
                'terrain',
                attrs={
                    'mesh': vr_top_fill_mesh,
                    'vr_only': True,
                    'lighting': False,
                    'color_texture': bgtex,
                },
            )
        )
        self.trees = bs.NodeActor(
            bs.newnode(
                'terrain',
                attrs={
                    'mesh': trees_mesh,
                    'lighting': False,
                    'reflection': 'char',
                    'reflection_scale': [0.1],
                    'color_texture': trees_texture,
                },
            )
        )
        self.bgterrain = bs.NodeActor(
            bs.newnode(
                'terrain',
                attrs={
                    'mesh': bgmesh,
                    'color': (0.92, 0.91, 0.9),
                    'lighting': False,
                    'background': True,
                    'color_texture': bgtex,
                },
            )
        )

        self._update_timer = bs.Timer(1.0, self._update, repeat=True)
        self._update()

        # Hopefully this won't hitch but lets space these out anyway.
        bui.add_clean_frame_callback(bs.WeakCall(self._start_preloads))

        random.seed()

        self._attract_mode_timer = bs.Timer(
            3.12, self._update_attract_mode, repeat=True
        )

        # Bring up the last place we were, or start at the main menu otherwise.
        with bs.ContextRef.empty():
            from bauiv1lib import specialoffer

            assert bs.app.classic is not None
            if bui.app.env.headless:
                # UI stuff fails now in headless builds; avoid it.
                pass
            elif bool(False):
                uicontroller = bs.app.ui_v1.controller
                assert uicontroller is not None
                uicontroller.show_main_menu()
            else:
                main_menu_location = bs.app.ui_v1.get_main_menu_location()

                # When coming back from a kiosk-mode game, jump to
                # the kiosk start screen.
                if env.demo or env.arcade:
                    # pylint: disable=cyclic-import
                    from bauiv1lib.kiosk import KioskWindow

                    bs.app.ui_v1.set_main_menu_window(
                        KioskWindow().get_root_widget(),
                        from_window=False,  # Disable check here.
                    )
                # ..or in normal cases go back to the main menu
                else:
                    if main_menu_location == 'Gather':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.gather import GatherWindow

                        bs.app.ui_v1.set_main_menu_window(
                            GatherWindow(transition=None).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    elif main_menu_location == 'Watch':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.watch import WatchWindow

                        bs.app.ui_v1.set_main_menu_window(
                            WatchWindow(transition=None).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    elif main_menu_location == 'Team Game Select':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.playlist.browser import (
                            PlaylistBrowserWindow,
                        )

                        bs.app.ui_v1.set_main_menu_window(
                            PlaylistBrowserWindow(
                                sessiontype=bs.DualTeamSession, transition=None
                            ).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    elif main_menu_location == 'Sillies Free-for-All Game Select':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.playlist.browser import (
                            PlaylistBrowserWindow,
                        )

                        bs.app.ui_v1.set_main_menu_window(
                            PlaylistBrowserWindow(
                                sessiontype=bs.FreeForAllSession,
                                transition=None,
                            ).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    elif main_menu_location == 'Coop Select':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.coop.browser import CoopBrowserWindow

                        bs.app.ui_v1.set_main_menu_window(
                            CoopBrowserWindow(
                                transition=None
                            ).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    elif main_menu_location == 'Benchmarks & Stress Tests':
                        # pylint: disable=cyclic-import
                        from bauiv1lib.debug import DebugWindow

                        bs.app.ui_v1.set_main_menu_window(
                            DebugWindow(transition=None).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )
                    else:
                        # pylint: disable=cyclic-import
                        from bauiv1lib.mainmenu import MainMenuWindow

                        bs.app.ui_v1.set_main_menu_window(
                            MainMenuWindow(transition=None).get_root_widget(),
                            from_window=False,  # Disable check here.
                        )

                # attempt to show any pending offers immediately.
                # If that doesn't work, try again in a few seconds
                # (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait
                # until the next opportunity.
                if not specialoffer.show_offer():

                    def try_again() -> None:
                        if not specialoffer.show_offer():
                            # Try one last time..
                            bui.apptimer(2.0, specialoffer.show_offer)

                    bui.apptimer(2.0, try_again)

        app.classic.main_menu_did_initial_transition = True

    def _update(self) -> None:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        app = bs.app
        env = app.env
        assert app.classic is not None

        # If language has changed, recreate our logo text/graphics.
        lang = app.lang.language
        if lang != self._language:
            self._language = lang
            y = 20
            base_scale = 1.1
            self._word_actors = []
            base_delay = 1.0
            delay = base_delay
            delay_inc = 0.02

            # Come on faster after the first time.
            if app.classic.main_menu_did_initial_transition:
                base_delay = 0.0
                delay = base_delay
                delay_inc = 0.02

            # We draw higher in kiosk mode (make sure to test this
            # when making adjustments) for now we're hard-coded for
            # a few languages.. should maybe look into generalizing this?..
            base_x = -20.0
            x = base_x - 20.0
            spacing = 5.0 * base_scale
            y_extra = 0.0
            x += spacing
            delay += delay_inc
            self._make_logo(
                20,
                125,
                1,
                delay=base_delay,
            )

    # Pop the logo and menu in.
    def _make_logo(
        self,
        x: float,
        y: float,
        scale: float,
        delay: float,
        jitter_scale: float = 1.0,
        rotate: float = 0.0,
        vr_depth_offset: float = 0.0,
    ) -> None:
        # pylint: disable=too-many-locals
        # Temp easter goodness.
        # LOGO
        ltex = bs.gettexture('textLogo')
        logo = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'texture': ltex,
                    'mesh_opaque': None,
                    'mesh_transparent': None,
                    'vr_depth': -10 + vr_depth_offset,
                    'rotate': rotate,
                    'attach': 'center',
                    'position': (-420, 240),
                    'scale': (250, 250),
                    'tilt_translate': 0.21,
                    'absolute_scale': True,
                },
            )
        )
        self._logo_node = logo.node
        self._word_actors.append(logo)
        if not bs.app.classic.main_menu_did_initial_transition:
            bs.animate(logo.node, 'opacity', {0.0: 0.0, 0.5: 1})

        # Sound
        bs.timer(delay+0.15, self._logo_sound.play)

        # Add a bit of stop-motion-y jitter to the logo
        # (unless we're in VR mode in which case its best to
        # leave things still).
        assert logo.node
        if not bs.app.env.vr:
            cmb = bs.newnode('combine', owner=logo.node, attrs={'size': 2})
            cmb.connectattr('output', logo.node, 'position')
            keys = {}
            time_v = 0.0

            # Gen some random keys for that stop-motion-y look
            for _i in range(10):
                keys[time_v] = x + (random.random() - 0.5) * 0.7 * jitter_scale
                time_v += random.random() * 0.1
            bs.animate(cmb, 'input0', keys, loop=True)
            keys = {}
            time_v = 0.0
            for _i in range(10):
                keys[time_v * self._ts] = (
                    y + (random.random() - 0.5) * 0.7 * jitter_scale
                )
                time_v += random.random() * 0.1
            bs.animate(cmb, 'input1', keys, loop=True)
        else:
            logo.node.position = (x, y)

        cmb = bs.newnode('combine', owner=logo.node, attrs={'size': 2})

        keys = {
            delay: 0.0,
            delay + 0.1: 700.0 * scale,
            delay + 0.2: 600.0 * scale,
        }
        bs.animate(cmb, 'input0', keys)
        bs.animate(cmb, 'input1', keys)
        cmb.connectattr('output', logo.node, 'scale')

    def _start_preloads(self) -> None:
        # FIXME: The func that calls us back doesn't save/restore state
        #  or check for a dead activity so we have to do that ourself.
        if self.expired:
            return
        with self.context:
            _preload1()

        def _start_menu_music() -> None:
            assert bs.app.classic is not None
            bs.setmusic(bs.MusicType.MENU)

        bui.apptimer(0.5, _start_menu_music)

    def _update_attract_mode(self) -> None:
        if bui.app.classic is None:
            return

        if not bui.app.config.resolve('Show Demos When Idle'):
            return

        threshold = 20.0

        # If we're idle *and* have been in this activity for that long,
        # flip over to our cpu demo.
        if bui.get_input_idle_time() > threshold and bs.time() > threshold:
            bui.app.classic.run_stress_test(
                playlist_type='Random',
                playlist_name='__default__',
                player_count=8,
                round_duration=20,
                attract_mode=True,
            )



def _preload1() -> None:
    """Pre-load some assets a second or two into the main menu.

    Helps avoid hitches later on.
    """
    for mname in [
        'plasticEyesTransparent',
        'playerLineup1Transparent',
        'playerLineup2Transparent',
        'playerLineup3Transparent',
        'playerLineup4Transparent',
        'angryComputerTransparent',
        'scrollWidgetShort',
        'windowBGBlotch',
    ]:
        bs.getmesh(mname)
    for tname in ['playerLineup', 'lock']:
        bs.gettexture(tname)
    for tex in [
        'iconRunaround',
        'iconOnslaught',
        'medalComplete',
        'medalBronze',
        'medalSilver',
        'medalGold',
        'characterIconMask',
    ]:
        bs.gettexture(tex)
    bs.gettexture('bg')
    from bascenev1lib.actor.powerupbox import PowerupBoxFactory

    PowerupBoxFactory.get()
    bui.apptimer(0.1, _preload2)


def _preload2() -> None:
    # FIXME: Could integrate these loads with the classes that use them
    #  so they don't have to redundantly call the load
    #  (even if the actual result is cached).
    for mname in ['powerup', 'powerupSimple']:
        bs.getmesh(mname)
    for tname in [
        'powerupBomb',
        'powerupSpeed',
        'powerupPunch',
        'powerupIceBombs',
        'powerupStickyBombs',
        'powerupShield',
        'powerupImpactBombs',
        'powerupHealth',
    ]:
        bs.gettexture(tname)
    for sname in [
        'powerup01',
        'boxDrop',
        'boxingBell',
        'scoreHit01',
        'scoreHit02',
        'dripity',
        'spawn',
        'gong',
    ]:
        bs.getsound(sname)
    from bascenev1lib.actor.bomb import BombFactory

    BombFactory.get()
    bui.apptimer(0.1, _preload3)


def _preload3() -> None:
    from sillies.silly.silly_factory import SillyFactory

    for mname in ['bomb', 'bombSticky', 'impactBomb']:
        bs.getmesh(mname)
    for tname in [
        'bombColor',
        'bombColorIce',
        'bombStickyColor',
        'impactBombColor',
        'impactBombColorLit',
    ]:
        bs.gettexture(tname)
    for sname in ['freeze', 'fuse01', 'activateBeep', 'warnBeep']:
        bs.getsound(sname)
    SillyFactory.get()
    bui.apptimer(0.2, _preload4)


def _preload4() -> None:
    for tname in ['bar', 'meter', 'null', 'flagColor', 'achievementOutline']:
        bs.gettexture(tname)
    for mname in ['frameInset', 'meterTransparent', 'achievementOutline']:
        bs.getmesh(mname)
    for sname in ['metalHit', 'metalSkid', 'refWhistle', 'achievement']:
        bs.getsound(sname)
    from bascenev1lib.actor.flag import FlagFactory

    FlagFactory.get()

first_run = True

class SplashScreenActivity(bs.Activity[bs.Player, bs.Team]):
    def __init__(self, settings: dict):
        super().__init__(settings)
        self._duration = 3

        bui.lock_all_input()

        self._tex = bs.gettexture('squarehairLogo')

    def _start_preloads(self) -> None:
        # FIXME: The func that calls us back doesn't save/restore state
        #  or check for a dead activity so we have to do that ourself.
        if self.expired:
            return
        with self.context:
            _preload1()

    def on_transition_in(self) -> None:
        from bascenev1lib.actor.splashbackground import SplashBackground
        from bascenev1lib.actor.image import Image
        self._ding_sound: bs.Sound = bs.getsound('squareHairSound')
        bs.timer(0.5, self._ding_sound.play)
        bs.Activity.on_transition_in(self)
        bui.add_clean_frame_callback(bs.WeakCall(self._start_preloads))
        self._background = SplashBackground(fade_time=0.3, start_faded=True, show_logo=False)
        position_image = (0,10)
        self._image = Image(self._tex,
                            transition='fadeOut',
                            position=position_image,
                            scale=(600, 600),
                            transition_delay=3,
                            transition_out_delay=self._duration-1.3
                        ).autoretain()
        bs.animate(self._image.node, 'opacity', {2.7: 1, 3: 0})
        bs.timer(self._duration, self.safe_end)

    def safe_end(self):
        bui.unlock_all_input()
        self.end()

first_run = True

class MainMenuSession(bs.Session):
    """Session that runs the main menu environment."""

    def __init__(self) -> None:
        # Gather dependencies we'll need (just our activity).
        self._activity_deps = bs.DependencySet(bs.Dependency(MainMenuActivity))

        super().__init__([self._activity_deps])
        self._locked = False
        app = bs.app
        global first_run

        import bauiv1 as bui
        if (
            not app.classic.main_menu_did_initial_transition
            and bui.app.config.get('Sillies Dev Intro', True)
            ):
                self.setactivity(bs.newactivity(SplashScreenActivity))
        else:
            app.classic.main_menu_did_initial_transition = True
            self.setactivity(bs.newactivity(MainMenuActivity))
        first_run = False

    @override
    def on_activity_end(self, activity: bs.Activity, results: Any) -> None:
        if self._locked:
            bui.unlock_all_input()

        # Any ending activity leads us into the main menu one.
        self.setactivity(bs.newactivity(MainMenuActivity))

    @override
    def on_player_request(self, player: bs.SessionPlayer) -> bool:
        # Reject all player requests.
        return False
