#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


""" This is a jcliff module, wrapping the utility Java tool JCliff
    in order to have Ansible supports fine tuning of Wildfly / JBoss
    EAP server configuration (subsystems)"""
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
    jcliff_command_line = ["bash", "-x",
                           data["jcliff"], "--cli=" +
                           data['wfly_home'] + "/bin/jboss-cli.sh",
                           "--ruledir=" + data['rules_dir'],
                           "--controller=" +
                           data['management_host'] + ":" +
                           data['management_port'],
                           "-v"]

    if data["management_username"] is not None:
        jcliff_command_line.extend(["--user=" + data["management_username"]])
    if data["management_password"] is not None:
        jcliff_command_line.extend(
            ["--password=" + data["management_password"]])

    jcliff_command_line.extend(list_rule_files(data['remote_rulesdir']))
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


def main():
    """ Main method for this module """
    default_jcliff_home = "/usr/share/jcliff"
    fields = dict(
        jcliff_home=dict(type='str', default=default_jcliff_home),
        jcliff=dict(default='/usr/bin/jcliff', type='str'),
        management_username=dict(required=False, type='str'),
        management_password=dict(required=False, type='str', no_log=True),
        rules_dir=dict(type='str', default=default_jcliff_home + "/rules"),
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
        subsystems=dict(type='list', required=False, elements='dict',
                        options=dict(
                            drivers=dict(type='list', required=False, elements='dict', options=dict(
                                driver_name=dict(type='str', required=True),
                                driver_module_name=dict(
                                    type='str', required=True),
                                driver_xa_datasource_class_name=dict(
                                    type='str', default='undefined'),
                                driver_class_name=dict(
                                    type='str', default='undefined'),
                                driver_datasource_class_name=dict(
                                    type='str', default='undefined'),
                                module_slot=dict(type='str', default='undefined'))),
                            datasources=dict(
                                type='list', required=False, elements='dict',
                                options=dict(
                                    name=dict(type='str', required=True),
                                    pool_name=dict(type='str', required=False),
                                    jndi_name=dict(type='str', required=True),
                                    use_java_context=dict(
                                        type='str', default='true'),
                                    connection_url=dict(
                                        type='str', required=True),
                                    driver_name=dict(
                                        type='str', required=True),
                                    enabled=dict(type='str', default='true'),
                                    password=dict(type='str', required=False),
                                    user_name=dict(type='str', required=False),
                                    max_pool_size=dict(
                                        type='str', default='undefined'),
                                    min_pool_size=dict(
                                        type='str', default='undefined'),
                                    idle_timeout_minutes=dict(
                                        type='str', default='undefined'),
                                    query_timeout=dict(
                                        type='str', default='undefined'),
                                    check_valid_connection_sql=dict(
                                        type='str', default='undefined'),
                                    validate_on_match=dict(type='str', default='undefined'))),
                            system_props=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=False),
                                    value=dict(type='str', required=False))),
                            deployments=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    artifact_id=dict(
                                        type='str', required=True),
                                    name=dict(type='str', required=False),
                                    path=dict(type='str', required=True))))),
        state=dict(default="present", choices=[
                   'present', 'absent'], type='str')
    )
    module = AnsibleModule(argument_spec=fields)

    if os.environ.get("JCLIFF_HOME"):
        module.params["jcliff_home"] = os.environ.get("JCLIFF_HOME")

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
