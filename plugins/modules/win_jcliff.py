#!/usr/bin/python
# -*- coding: utf-8 -*

# (c) 2020, Red Hat, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''

module: win_jcliff

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

  subsystems:
    description:
      - Wildfly or JBoss EAP Subsystems.
    type: list
    suboptions:

      drivers:
        description:
          - JDBC driver configurations.
        type: list
        suboptions:

          driver_name:
            description:
              - Name of the driver.
            type: str
            required: True

          driver_module_name:
            description:
              - Name of the driver module.
            type: str
            required: True

          driver_xa_datasource_class_name:
            description:
              - Class name for the XA datasource.
            type: str
            default: 'undefined'

          driver_class_name:
            description:
              - Driver class name.
            type: str
            default: 'undefined'

          driver_datasource_class_name:
            description:
              - Class name for the datasource.
            type: str
            default: 'undefined'

          module_slot:
            description:
              - Name of the module slot.
            type: str
            default: 'undefined'

      datasources:
        description:
          - Datasource configurations.
        type: list
        suboptions:

          name:
            description:
              - Datasource name.
            type: str
            required: True

          pool_name:
            description:
              - Name of the datasource pool.
            type: str

          jndi_name:
            description:
              - JNDI name.
            type: str
            required: True

          use_java_context:
            description:
              - Use the Java context.
            type: str
            default: 'true'

          connection_url:
            description:
              - Connection URL.
            type: str
            required: True

          driver_name:
            description:
              - Name of the driver.
            type: str
            required: True

          enabled:
            description:
              - Whether the datasource is enabled.
            type: str
            default: 'true'

          password:
            description:
              - Datasource password.
            type: str

          user_name:
            description:
              - Datasource user name.
            type: str

          max_pool_size:
            description:
              - Datasource maximum pool size.
            type: str
            default: 'undefined'

          min_pool_size:
            description:
              - Datasource minimum pool size.
            type: str
            default: 'undefined'

          idle_timeout_minutes:
            description:
              - Datasource idle timeout minutes.
            type: str
            default: 'undefined'

          query_timeout:
            description:
              - Datasource query timeout.
            type: str
            default: 'undefined'

          check_valid_connection_sql:
            description:
              - Datasource SQL query for checking a valid connection.
            type: str
            default: 'undefined'

          validate_on_match:
            description:
              - Datasource validate on match.
            type: str
            default: 'undefined'

      system_props:
        description:
          - System properties.
        type: list
        suboptions:

          name:
            description:
              - System property name.
            type: str

          value:
            description:
              - System property value.
            type: str

      deployments:
        description:
          - Deployments.
        type: list
        suboptions:

          name:
            description:
              - Name of the deployment.
            type: str

          path:
            description:
              - Path to the deployment.
            type: str
            required: True

          disabled:
            description:
              - Adds to the repository in a disabled state.
            type: bool
            required: False

          runtime_name:
            description:
              - Runtime of the deployment.
            type: str
            required: False

          replace_name_regex:
            description:
              - Regex pattern to replace the deployment if the value matches the name.
            type: str
            required: False

          replace_runtime_name_regex:
            description:
              - Regex pattern to replace the deployment if the value matches the runtime name.
            type: str
            required: False

          unmanaged:
            description:
              - Specifies whether the deployment should be managed.
            type: bool
            required: False

      keycloak:
        description:
          - Keycloak.
        type: list
        suboptions:

          secure_deployment:
            description:
              - List of applications to secure using Keycloak.
            type: list
            suboptions:

              deployment_name:
                description:
                  - Name of the deployment.
                type: str
                required: True

              resource:
                description:
                  - The client-id of the application.
                type: str
                required: True

              auth_server_url:
                description:
                  - Base URL of the Keycloak server.
                type: str
                required: True

              realm:
                description:
                  - Name of the Keycloak realm.
                type: str

              ssl_required:
                description:
                  - Ensures that all communication to and from the Keycloak server is over HTTPS.
                type: str

              verify_token_audience:
                description:
                  - Whether the adapter will verify whether the token contains this client name (resource) as an audience.
                type: bool

              use_resource_role_mappings:
                description:
                  - Whether the adapter will look inside the token for application level role mappings for the user.
                type: bool

              credential:
                description:
                  - The secure value for the application.
                type: str
      logging:
        description:
          - logger.
        type: list
        suboptions:
          name:
            description:
              - Replace name with name of the log category
            type: str
            required: True
          level:
            description:
              - Replace level with log level that is to be set
            type: str
            required: False

'''

EXAMPLES = '''
- name: Configure Wildfly instance
  jcliff:
    wfly_home: "/opt/wildfly"
    subsystems:
      - system_props:
          - name: jcliff.enabled
            value: 'enabled.plus'
      - datasources:
          - name: ExampleDS2
            use_java_context: 'true'
            jndi_name: java:jboss/datasources/ExampleDS2
            connection_url: "jdbc:h2:mem:test2;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE"
            driver_name: h2
'''
