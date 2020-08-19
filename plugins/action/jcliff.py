from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


""" This action module use JCliff rule templates to
    render directive before transfering them as rule
    file to the target host. """
import os
import tempfile

from ansible.plugins.action import ActionBase
from ansible.template import Templar
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


class ActionModule(ActionBase):
    """ JCliff action module """
    TRANSFERS_FILES = True
    TARGET_FILENAME_SUFFIX = ".jcliff.yml"

    def _template_from_jinja_to_yml(self, template_name, subsystem_values):
        templates = self._loader.path_dwim_relative(self._loader.get_basedir(),
                                                    'templates/rules', template_name)
        if not os.path.isfile(templates):
            templates = _get_role_home() + '/templates/rules/' + template_name

        with open(templates, 'r') as file:
            data = file.read()
        templar = Templar(loader=self._loader, variables=subsystem_values)
        return _write_template_result_to_file(templar.template(data))

    def _deploy_custom_rules_if_any(self, tmp_remote_src):
        if 'rule_file' in self._task.args:
            custom_rulesdir = self._task.args['rule_file']
            if custom_rulesdir is not None:
                for custom_rule_file in os.listdir(custom_rulesdir):
                    self._transfer_file(custom_rulesdir + "/" + custom_rule_file,
                                        tmp_remote_src + custom_rule_file +
                                        "-custom" + self.TARGET_FILENAME_SUFFIX)

    def _build_and_deploy_jcliff_rule_files(self, tmp_remote_src):
        template_name_by_subsys = {
            'drivers': 'drivers.j2',
            'datasources': 'datasource.j2',
            'system_props': 'system-properties.j2',
            'deployments': 'deployments.j2',
            'logging': 'logging.j2',
            'mail': 'mail.j2',
            'scanner': 'scanner.j2',
            'transactions': 'transactions.j2',
            'keycloak': 'keycloak.j2'
        }
        subsystems = self._task.args['subsystems']
        if subsystems is not None:
            for subsys in subsystems:
                for key in subsys.keys():
                    if key in ('drivers', 'datasources', 'keycloak'):
                        for index, subsystem_values in enumerate(subsys[key]):
                            self._transfer_file(
                                self._template_from_jinja_to_yml(
                                    template_name_by_subsys[key],
                                    {"values": subsystem_values}),
                                tmp_remote_src + key + "-" +
                                str(index) + self.TARGET_FILENAME_SUFFIX)
                    if key in ('system_props', 'deployments', 'logging', 'mail', 'scanner', 'transactions'):
                        self._transfer_file(self._template_from_jinja_to_yml(
                            template_name_by_subsys[key], {"values": subsys[key]}),
                            tmp_remote_src + key + self.TARGET_FILENAME_SUFFIX)

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
