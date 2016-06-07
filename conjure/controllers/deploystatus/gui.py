from conjure.ui.views.deploystatus import DeployStatusView
from ubuntui.ev import EventLoop
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from . import common
import os.path as path
import os
import sys


this = sys.modules[__name__]
this.view = None
this.pre_exec_pollinate = False
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)


def __fatal(error):
    return __handle_exception('ED', Exception(error))


def finish():
    deploy_done_sh = os.path.join(this.bundle_scripts,
                                  '00_deploy-done.sh')
    common.wait_for_applications(deploy_done_sh,
                                 __fatal,
                                 app.ui.set_footer)
    return controllers.use('steps').render()


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)


def __refresh(*args):
    this.view.refresh_nodes()
    EventLoop.set_alarm_in(1, __refresh)


def render():
    """ Render deploy status view
    """
    this.view = DeployStatusView(app)

    try:
        name = app.config['metadata']['friendly-name']
    except KeyError:
        name = app.config['spell']
    app.ui.set_header(
        title="Conjuring up {}".format(
            name)
    )
    app.ui.set_body(this.view)
    EventLoop.set_alarm_in(1, __refresh)
    finish()