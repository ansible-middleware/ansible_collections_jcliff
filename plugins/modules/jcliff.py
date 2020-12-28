#!/usr/bin/python
# -*- coding: utf-8 -*

# (c) 2020, Red Hat, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''

module: jcliff

author: Andrew Block (@sabre1041), Romain Pelisse (@rpelisse)

short_description: Manages the configuration of Wildfly / JBoss EAP servers

description:
- Wraps the JCliff Java utility tool in order to support fine grained tuning
  of Wildfly / JBoss EAP server configuration in Ansible.

options:

  jcliff_home:
    description:
      - Home directory for the Jcliff utility.
    type: str
    default: '/usr/share/jcliff'

  jcliff:
    description:
      - Path to the the Jcliff utility.
    type: str
    default: '/usr/bin/jcliff'

  management_username:
    description:
      - Management username.
    type: str

  management_password:
    description:
      - Management password.
    type: str

  rules_dir:
    description:
      - Directory containing Jcliff rules.
    type: str
    default: '/usr/share/jcliff/rules'

  wfly_home:
    description:
      - Home directory for the Wildfly or JBoss EAP server.
    type: str
    aliases: ['jboss_home']

  management_host:
    description:
      - Management host.
    type: str
    default: 'localhost'

  management_port:
    description:
      - Management port.
    type: str
    default: '9990'

  jcliff_jvm:
    description:
      - Location of the Java JVM.
    type: str

  rule_file:
    description:
      - Name of the rules file.
    type: str

  remote_rulesdir:
    description:
      - Location of the rules directory on the remote instance.
    type: str

  debug_mode:
    description:
      - Debug output.
    type: bool
    default: False

  timeout:
    description:
      - Set jcliff timeout (how long a jcliff will allow a query to the server to last)
    type: int
    default: 30000

  state:
    description:
      - If 'present', configurations will be applied to the Wildfly/JBoss EAP server.
      - If 'absent', configurations will be removed from the Wildfly/JBoss EAP server - this is NOT implemented yet!
    type: str
    default: 'present'
    choices: ['present','absent']

  components:
    description:
      - Wildfly or JBoss EAP configuration components in JCliff compatible format
    aliases: ['subsystems']
'''

EXAMPLES = '''
- name: Configure Wildfly instance
  jcliff:
    wfly_home: "/opt/wildfly"
    subsystems:
      - system_properties:
          - name: jcliff.enabled
            value: 'enabled.plus'
      - datasources:
          - name: ExampleDS2
            use_java_context: 'true'
            jndi_name: java:jboss/datasources/ExampleDS2
            connection_url: "jdbc:h2:mem:test2;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE"
            driver_name: h2
'''


import subprocess
import os
import os.path

from ansible.module_utils.basic import AnsibleModule


def check_if_folder_exists(module, param_key):
    path = module.params[param_key]
    if not os.path.isdir(path):
        module.fail_json(msg="%s is invalid: %s " % (param_key, path))


def list_rule_files(rulesdir):
    """ list all the files inside the rule's directory """
    rules_filename = os.listdir(rulesdir)
    rule_files = []
    for filename in rules_filename:
        if filename.endswith("jcliff.yml"):
            rule_files.append(rulesdir + "/" + filename)
    return rule_files


def add_to_env(name, value):
    """ add provided variables to environnement """
    if value is not None:
        os.environ[name] = value


def define_status_based_on_server_configuration_changes(output):
    if "Server configuration changed: true" in output:
        return 2
    return 0


def execute_rules_with_jcliff(data):
    """ execute the rules provided using jcliff """

    listed_rules_files = list_rule_files(data['remote_rulesdir'])

    if len(listed_rules_files) == 0:
        return {"rc": 0, "msg": "No Components Provided"}, 0

    jcliff_command_line = ["bash", "-x",
                           data["jcliff"], "--cli=" +
                           data['wfly_home'] + "/bin/jboss-cli.sh",
                           "--ruledir=" + data['rules_dir'],
                           "--timeout=" + str(data['timeout']),
                           "--controller=" +
                           data['management_host'] + ":" +
                           data['management_port'],
                           "-v"]

    if data["management_username"] is not None:
        jcliff_command_line.extend(["--user=" + data["management_username"]])
    if data["management_password"] is not None:
        jcliff_command_line.extend(
            ["--password=" + data["management_password"]])

    jcliff_command_line.extend(listed_rules_files)
    output = None
    status = "undefined"
    add_to_env('JAVA_HOME', data['jcliff_jvm'])
    add_to_env('JBOSS_HOME', data['wfly_home'])
    add_to_env('JCLIFF_HOME', data['jcliff_home'])

    try:
        output = subprocess.check_output(jcliff_command_line,
                                         stderr=subprocess.STDOUT,
                                         shell=False,
                                         env=os.environ)
        status = define_status_based_on_server_configuration_changes(
            output.decode())
    except subprocess.CalledProcessError as jcliffexc:
        error = jcliffexc.output.decode()
        if (jcliffexc.returncode != 2) and (jcliffexc.returncode != 0):
            return {"failed": True, "report":
                    {"status": jcliffexc.returncode,
                     "output": output,
                     "jcliff_cli": jcliff_command_line,
                     "JAVA_HOME": os.getenv("JAVA_HOME", "Not defined"),
                     "JCLIFF_HOME": os.getenv("JCLIFF_HOME", "Not defined"),
                     "JBOSS_HOME": os.getenv("JBOSS_HOME", "Not defined"),
                     "error": error}}, jcliffexc.returncode
        return {"present:": error}, 2
    except Exception as exception:
        output = exception
        status = 1
    if status == 0:
        return {"present": output, "rc": status, "jcliff_cli": jcliff_command_line}, status
    return {"failed": True,
            "report": output,
            "rc": status,
            "jcliff_cli": jcliff_command_line}, status


def ansible_result_from_status(status):
    """ extract the ansible result from the status returned by jcliff """
    has_changed = False
    has_failed = False
    if status == 2:
        has_changed = True
    if status not in (0, 2):
        has_failed = True
    return (has_changed, has_failed)


def jcliff_present(data):
    """ implement ansible present state using jcliff """
    meta, status = execute_rules_with_jcliff(data)
    has_changed, has_failed = ansible_result_from_status(status)
    return (has_changed, has_failed, meta)


def jcliff_absent(data=None):
    """ jcliff and this module does NOT support the absent state """
    return {"absent": "not yet implemented", "data": data}


def list_dict(value):
    """ verify the type is a list or dict """
    if isinstance(value, (list, dict)):
        return value
    raise TypeError


def main():
    """ Main method for this module """
    default_jcliff_home = "/usr/share/jcliff"
    default_path_to_jcliff = "/usr/bin/jcliff"
    default_rules_dir = default_jcliff_home + "/rules"
    fields = dict(
        jcliff_home=dict(type='str', default=default_jcliff_home),
        jcliff=dict(default=default_path_to_jcliff, type='str'),
        management_username=dict(required=False, type='str'),
        management_password=dict(required=False, type='str', no_log=True),
        rules_dir=dict(type='str', default=default_rules_dir),
        wfly_home=dict(required=True, aliases=['jboss_home'], type='str'),
        management_host=dict(default='localhost', type='str'),
        management_port=dict(default='9990', type='str'),
        jcliff_jvm=dict(default=os.getenv("JAVA_HOME", None),
                        type='str', required=False),
        rule_file=dict(required=False, type='str'),
        # do not use the following parameter, value is provided by the actions plugin
        # any value defined in the playbook will simply be ignored
        remote_rulesdir=dict(required=False, type='str'),
        # Careful, switching to 'True' will mean each run of the module will create temporary files that it will NOT be deleted!
        debug_mode=dict(required=False, type='bool', default=False),
        timeout=dict(required=False, type='int', default=30000),
        components=dict(type=list_dict, aliases=['subsystems'], required=False),
        state=dict(default="present", choices=[
                   'present', 'absent'], type='str')
    )
    module = AnsibleModule(argument_spec=fields)
    # allow env var to override value set in module
    module.params["jcliff_home"] = os.getenv("JCLIFF_HOME", module.params["jcliff_home"])

    # if JCLIFF_HOME is not set to default value, we need to recompute
    # other related default valueswe need to compute the "new" default value
    # unless they have been already redefined
    if module.params["jcliff_home"] != default_jcliff_home:
        if module.params["jcliff"] == default_path_to_jcliff:
            module.params["jcliff"] = module.params["jcliff_home"] + "/jcliff"
        if module.params["rules_dir"] == default_rules_dir:
            module.params["rules_dir"] = module.params["jcliff_home"] + "/rules"

    check_if_folder_exists(module, "jcliff_home")
    check_if_folder_exists(module, "wfly_home")
    if not module.params["jcliff_jvm"] is None:
        check_if_folder_exists(module, "jcliff_jvm")
    check_if_folder_exists(module, "rules_dir")

    choice_map = {
        "present": jcliff_present,
        "absent": jcliff_absent,
    }
    has_changed, has_failed, result = choice_map.get(
        module.params['state'])(data=module.params)
    module.exit_json(changed=has_changed, failed=has_failed, meta=result)


if __name__ == '__main__':
    main()
