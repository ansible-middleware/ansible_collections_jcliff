from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


""" This action module use JCliff rule templates to
    render directive before transfering them as rule
    file to the target host. """
import os
import tempfile
import json

from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


def _write_template_result_to_file(content):
    tmp = tempfile.NamedTemporaryFile('w', delete=False)
    tmp.writelines(content)
    tmp.close()
    return tmp.name

# this is temporary workaround, until we figured out a proper way
# of doing this


def _get_role_home():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


def _unescape_keys(d):
    if isinstance(d, dict):
        new = {}
        for k, v in d.items():
            new[k.replace('_', '-')] = _unescape_keys(v)
        return new
    elif isinstance(d, list):
        new = []
        for v in d:
            new.append(_unescape_keys(v))
        return new
    else:
        return d


class ActionModule(ActionBase):
    """ JCliff action module """
    TRANSFERS_FILES = True
    TARGET_FILENAME_SUFFIX = ".jcliff.yml"

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)

    def _deploy_custom_rules_if_any(self, tmp_remote_src):
        if 'rule_file' in self._task.args:
            custom_rulesdir = self._task.args['rule_file']
            if custom_rulesdir is not None:
                for custom_rule_file in os.listdir(custom_rulesdir):
                    self._transfer_file(custom_rulesdir + "/" + custom_rule_file,
                                        tmp_remote_src + custom_rule_file +
                                        "-custom" + self.TARGET_FILENAME_SUFFIX)

    def _build_and_deploy_jcliff_rule_files(self, tmp_remote_src):
        display.vvvv(u"Build and deploy jcliff rule tmpfile: %s" % tmp_remote_src)

        components = self._get_component_list(self._task.args.get('components', self._task.args.get('subsystems')))

        if components is not None:
            for idx, component in enumerate(components):
                display.vvvv(u"Component ID: %s" % component)

                component_jcliff_content = json.dumps(_unescape_keys(component), separators=(',', '=>'))
                display.vvvv(u"JCliff Component Content: %s" % component_jcliff_content)

                self._transfer_file(_write_template_result_to_file(component_jcliff_content),
                                    tmp_remote_src + str(idx) + self.TARGET_FILENAME_SUFFIX)

    def _get_component_list(self, input_component):
        if isinstance(input_component, dict):
            return [input_component]

        return input_component

    def run(self, tmp=None, task_vars=None):
        tmp_remote_src = self._make_tmp_path()
        self._build_and_deploy_jcliff_rule_files(tmp_remote_src)
        self._deploy_custom_rules_if_any(tmp_remote_src)
        result = super(ActionModule, self).run(tmp, task_vars)
        new_module_args = self._task.args.copy()
        new_module_args.update(dict(remote_rulesdir=tmp_remote_src,))
        result.update(self._execute_module(
            module_name='jcliff', module_args=new_module_args, task_vars=task_vars))
        if 'debug_mode' in self._task.args and not self._task.args['debug_mode']:
            self._remove_tmp_path(self._connection._shell.tmpdir)
        return result
