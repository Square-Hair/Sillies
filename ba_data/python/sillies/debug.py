import bascenev1 as bs
import _baplus
import babase

def yes(*args, **kwargs): return True

def send(msg: str, condition: bool = True) -> None:
    """Print something on-screen and log it in console."""
    if not condition:
        return
    # Get source file's name
    import inspect
    source = (
        inspect.getmodule(inspect.stack()[1][0]).__name__ or 'file'
        + '.py'
    )
    # Send the messages wherever!
    print(f"[{source}]: {msg}")
    bui.screenmessage(f'{msg}')

def enable_pro():
    """ Enables BombSquad Pro. """
    babase.app.classic.accounts.have_pro = yes
    _baplus.get_purchased = yes

import babase
import babase._devconsole as devconsole
import bauiv1 as bui
class SilliesConsoleTabsInit:
    """ Library of custom console tabs. """

    """ Tab classes. """
    class DevToolsTab(devconsole.DevConsoleTab):
        def __init__(self) -> None:
            # Push the buttons!
            ## Quit
            btn_x = -595
            self.button(
                'Quit',
                (btn_x,10),
                (80,30),
                style='dark',
                call=self.quit
                )
            ## Square Hair Intro toggle
            btn_x += 110
            self.button(
                f'Toggle Square Hair Intro',
                (btn_x,10),
                (300,30),
                style='dark',
                call=self.toggle_dev_intro
                )
            ## Launch Game
            btn_x += 330
            self.button(
                'Launch Game',
                (btn_x,10),
                (180,30),
                style='dark',
                call=self.launch_mode_window
                )
            ## Toggle chat printing
            btn_x += 210
            self.button(
                f'Toggle Chat Logs',
                (btn_x,10),
                (220,30),
                style='dark',
                call=self.toggle_chat_logs
                )


        """ Tab button functions. """
        def button_sfx(self) -> None: bui.getsound('gunCocking').play()

        def quit(self) -> None:
            """ Quits the game. """
            self.button_sfx() # Play a cool SFX
            bui.quit(confirm=False, quit_type=bui.QuitType.HARD) # Yeah.

        def launch_mode_window(self) -> None:
            """Open our launch window."""
            # Play a cool SFX.
            self.button_sfx()
            # Open our LaunchModeTab window.
            from eon.ui.launch import LaunchModeTab
            LaunchModeTab()

        def toggle_dev_intro(self) -> None:
            """ Toggles whether we play the square hair intro or not. """
            v = bui.app.config['Sillies Dev Intro'] = not bui.app.config.get('Sillies Dev Intro', True)
            bui.screenmessage(
                f'Square Hair Team intro will be {"played" if v else "skipped"} from now on!',
                color=(1,1,0),
            )
            bui.getsound('gunCocking').play()
            bui.app.config.commit()

        def toggle_chat_logs(self) -> None:
            """ Toggles whether we save chat logs in console. """
            v = bui.app.config['Sillies Chat Logs'] = not bui.app.config.get('Sillies Chat Logs', False)
            bui.screenmessage(
                f'Chat logs {"will be" if v else "will not be"} saved in the console :)',
                color=(1,1,0),
            )
            bui.getsound('gunCocking').play()
            bui.app.config.commit()


    """ Mixed functions. """
    def _add_console_tabs(self) -> None:
        """ Appends some developer tools into the game's F2 console. """
        babase.app.devconsole.tabs.append(devconsole.DevConsoleTabEntry('DevTools', self.DevToolsTab))
