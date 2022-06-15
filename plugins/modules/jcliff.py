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

author: Andrew Block (@sabre1041), Romain Pelisse (@rpelisse), Harsha Cherukuri (@hcheruku)

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
    required: True

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

  reconnect_delay:
    description:
      - Set jcliff reconnect delay
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
      - Wildfly or JBoss EAP Subsystems or configuration component
    type: list
    elements: dict
    aliases: ['subsystems']
    suboptions:
      drivers:
        description:
          - JDBC driver configurations.
        type: list
        elements: dict
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
        elements: dict
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

      xadatasources:
        description:
          - XA Datasource configurations.
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

          xa_datasource_properties:
            description:
              - Properties for XA datasource
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

          no_recovery:
            description:
              - Should datasource attempt recovery.
            type: bool
            default: 'undefined'

          validate_on_match:
            description:
              - 
            type: bool
            default: 'undefined'

          background_validation:
            description:
              - The validate-on-match element indicates whether or not 
                connection level validation should be done when a connection 
                factory attempts to match a managed connection for a given set.
            type: bool
            default: 'undefined'
            
          valid_connection_checker_class_name:
            description:
              - An org.jboss.jca.adapters.jdbc.ValidConnectionChecker that 
                provides a SQLException isValidConnection(Connection e) method 
                to validate is a connection is valid.
            type: str
            default: 'undefined'

          check_valid_connection_sql:
            description:
              - Datasource SQL query for checking a valid connection.
            type: str
            default: 'undefined'

          exception_sorter_class_name:
            description:
              - Which exception sorter class should be used.
            type: str
            default: 'undefined'
          
          same_rm_override:
            description:
              - The same-rm-override element allows one to unconditionally set 
                whether the javax.transaction.xa.XAResource.isSameRM(XAResource) 
                returns true or false.
            type: bool
            default: 'undefined'
            
          background_validation_millis:
            description:
              - The background-validation-millis element specifies the amount of 
                time, in milliseconds, that background validation will run. 
                Changing this value require a server restart.
            type: int
            default: 'undefined'

      system_properties:
        description:
          - System properties.
        type: list
        elements: dict
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
        elements: dict
        suboptions:
          name:
            description:
              - Name of the deployment.
            type: str
            required: True
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

      interfaces:
        description:
          - Interface.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name of the interface
            type: str
            required: True
          any_address:
            description:
              - Sockets using this interface should be bound to a wildcard address
            type: bool
            required: False
          inet_address:
            description:
              - Whether or not the address matches the given value
            type: str
            required: False
          link_local_address:
            description:
              - Part of the selection criteria for choosing an IP address for this interface should be whether or not the address is link-local
            type: bool
            required: False
          loopback:
            description:
              - Part of the selection criteria for choosing an IP address for this interface should be whether or not it is a loopback address
            type: bool
            required: False
          loopback_address:
            description:
              - Value indicating that the IP address for this interface should be the given value, if a loopback interface exists on the machine
            type: str
            required: False
          multicast:
            description:
              - Whether or not its network interface supports multicast
            type: bool
            required: False
          nic:
            description:
              - Part of the selection criteria for choosing an IP address for this interface should be whether its network interface has the given name
            type: str
            required: False
          nic_match:
            description:
              -  Whether its network interface has a name that matches the given regular expression
            type: str
            required: False
          point_to_point:
            description:
              - Whether or not its network interface is a point-to-point interface
            type: bool
            required: False
          public_address:
            description:
              - Whether or not it is a publicly routable address
            type: bool
            required: False
          resolved_address:
            description:
              - The resolved ip address for this interface
            type: str
            required: False
          site_local_address:
            description:
              - Whether or it is a site-local address
            type: bool
            required: False
          subnet_match:
            description:
              - Whether or it the address fits in the given subnet definition. Value is a network IP address and the number of bits in the address
            type: str
            required: False
          up:
            description:
              - Whether its network interface is currently up
            type: bool
            required: False
          virtual:
            description:
              - Whether its network interface is a virtual interface
            type: bool
            required: False

      keycloak:
        description:
          - Keycloak.
        type: list
        elements: dict
        suboptions:

          secure_deployment:
            description:
              - List of applications to secure using Keycloak.
            type: list
            elements: dict
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
                  - Ensures that communication to and from the Keycloak server is over HTTPS. Default external. Possible values all external none.
                type: str

              verify_token_audience:
                description:
                  - Whether the adapter will verify whether the token contains this client name (resource) as an audience. Default is false.
                type: bool

              use_resource_role_mappings:
                description:
                  - Whether the adapter will look inside the token for application level role mappings for the user. The default value is false.
                type: bool

              credential:
                description:
                  - The secure value for the application. If not provided, it is setup as a public client.
                type: str

              disable_trust_manager:
                description:
                  - Should only be used during development and NEVER in production as it will disable verification of SSL certificates. Default false.
                type: bool

              # enable_cors:
              #   description:
              #     - Enables CORS support. It will handle CORS preflight requests and look into the access token to determine valid origins. Default false.
              #   type: bool
      logging:
        description:
          - logger.
        type: list
        elements: dict
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
      mail:
        description:
          - mail.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Replace name with subject.
            type: str
            required: True
          from_email:
            description:
              - Replace from_email with email id.
            type: str
            required: True
          jndi_name:
            description:
              - Set jndi_name, for ex. java:jboss/mail/testSession
            type: str
            required: True
          outbound_socket_binding_ref:
            description:
              - Set outbound_socket_binding_ref, for ex. mail-smtp
            type: str
            required: True
          ssl:
            description:
              - Set ssl
            type: bool
            required: False

      modcluster:
        description:
          - Manage Modcluster.
        type: dict
        suboptions:
          proxy:
            description:
              - Modcluster proxy.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the modcluster proxy.
                type: str
                required: True
              listener:
                description:
                  - The name of Undertow listener that will be registered with the reverse proxy.
                type: str
                required: False
              advertise:
                description:
                  - Whether to enable multicast-based advertise mechanism.
                type: bool
                required: False
              advertise_security_key:
                description:
                  - If specified, reverse proxy advertisements checksums will be verified using this value as a salt.
                type: str
                required: False
              advertise_socket:
                description:
                  - Name of socket binding to use for the advertise socket.
                type: str
                required: False
              auto_enable_contexts:
                description:
                  - If false, the contexts are registered with the reverse proxy as disabled.
                type: bool
                required: False
              balancer:
                description:
                  - The name of the balancer on the reverse proxy to register with.
                type: str
                required: False
              excluded_contexts:
                description:
                  - List of contexts to exclude from registration with the reverse proxies.
                type: str
                required: False
              flush_packets:
                description:
                  - Whether to enable packet flushing on the reverse proxy.
                type: bool
                required: False
              flush_wait:
                description:
                  - Time to wait before flushing packets on the reverse proxy.
                type: int
                required: False
              load_balancing_group:
                description:
                  - Name of the load balancing group this node belongs to.
                type: str
                required: False
              max_attempts:
                description:
                  - Maximum number of failover attempts by reverse proxy when sending the request to the backend server.
                type: int
                required: False
              node_timeout:
                description:
                  - Timeout (in seconds) for proxy connections to a node. Time mod_cluster will wait for the back-end response before returning an error.
                type: int
                required: False
              ping:
                description:
                  - Number of seconds for which to wait for a pong answer to a ping.
                type: int
                required: False
              proxies:
                description:
                  - List of reverse proxies for mod_cluster to register with defined by 'outbound-socket-binding' in 'socket-binding-group'.
                type: list
                required: False
                elements: str
              proxy_list:
                description:
                  - List of reverse proxies to register with. Format (hostname:port) separated with commas.
                type: str
                required: False
              proxy_url:
                description:
                  - Base URL for MCMP requests.
                type: str
                required: False
              session_draining_strategy:
                description:
                  - Session draining strategy used during undeployment of a web application.
                type: str
                required: False
              simple_load_provider:
                description:
                  - Simple load provider returns constant pre-configured load balancing factor.
                type: int
                required: False
              smax:
                description:
                  - Soft maximum idle connection count for reverse proxy.
                type: int
                required: False
              socket_timeout:
                description:
                  - Timeout to wait for the reverse proxy to answer a MCMP message.
                type: int
                required: False
              ssl_context:
                description:
                  - Reference to the SSLContext to be used by mod_cluster.
                type: str
                required: False
              status_interval:
                description:
                  - Number of seconds a STATUS message is sent from the application server to the proxy.
                type: int
                required: False
              sticky_session:
                description:
                  - Indicates whether subsequent requests for a given session should be routed to the same node, if possible.
                type: bool
                required: False
              sticky_session_force:
                description:
                  - Whether the reverse proxy should run an error in the event that the balancer is unable to route a request to the node to which it is stuck.
                type: bool
                required: False
              sticky_session_remove:
                description:
                  - Whether the reverse proxy should remove session stickiness when the balancer is unable to route a request to the node to which it is stuck.
                type: bool
                required: False
              stop_context_timeout:
                description:
                  - Maximum time to wait for context to process pending requests.
                type: int
                required: False
              ttl:
                description:
                  - Time to live (in seconds) for idle connections above smax.
                type: int
                required: False
              worker_timeout:
                description:
                  - Number of seconds to wait for a worker to become available to handle a request.
                type: int
                required: False

      scanner:
        description:
          - The deployment scanner is only used in standalone mode.
          - It can be found in standalone.xml.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - The name of the scanner.
              - It can be path, relative-to, scan-enabled, scan-interval,
                auto-deploy-zipped, auto-deploy-exploded, auto-deploy-xml,
                deployment-timeout
            type: str
            required: False
          value:
            description:
              - enter the respective value,
                corresponding to name.
                https://docs.jboss.org/infinispan/9.4/serverconfigdocs/jboss-as-deployment-scanner_2_0.html
            type: str
            required: False

      transactions:
        description:
          - Setting node-identifier
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Node-identifier
            type: str
            required: True
          value:
            description:
              - enter the respective value, corresponding to name.
            type: str
            required: True

      standard_sockets:
        description:
          - Create Socket bindings.
        type: dict
        suboptions:
          socket_binding:
            description:
              - Socket bindings.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the socket configuration that should be used elsewhere in the configuration.
                type: str
                required: True
              port:
                description:
                  - Base port to which a socket based on this configuration should be bound.
                type: str
                required: True
              interface:
                description:
                  - Logical name of the interface to which a socket based on this configuration should be bound.
                type: str
                required: False
              multicast_address:
                description:
                  - If the socket will be used for multicast, the multicast address to use.
                type: str
                required: False
              multicast_port:
                description:
                  - If the socket will be used for multicast, the multicast port to use.
                type: str
                required: False
          remote_destination_outbound_socket_binding:
            description:
              - Remote destination outbound socket binding.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the remote destination outbound socket configuration that should be used elsewhere in the configuration.
                type: str
                required: True
              host:
                description:
                  - The host name or the IP address of the remote destination to which this outbound socket will connect.
                type: str
                required: True
              port:
                description:
                  - The port number of the remote destination to which the outbound socket should connect.
                type: int
                required: True
              fixed_source_port:
                description:
                  - Whether the port value should remain fixed even if numeric offsets are applied to the other outbound sockets in the socket group.
                type: bool
                required: False
              source_interface:
                description:
                  - The name of the interface which will be used for the source address of the outbound socket.
                type: str
                required: False
              source_port:
                description:
                  - The port number which will be used as the source port of the outbound socket.
                type: int
                required: False

      messaging_activemq:
        description:
          - Create messaging activemq.
        type: dict
        suboptions:
          server_property:
            description:
              - Creates and sets messaging-activemq server properties.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Name of property.
                type: str
                required: True
              value:
                description:
                  - Value of property.
                type: str
                required: True
          jms_queue:
            description:
              - Create JMS queue
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the jms queue
                type: str
                required: True
              entries:
                description:
                  - Enter the required entries.
                type: list
                elements: str
                required: True
              durable:
                description:
                  - Enter if it is durable or not.
                type: str
                required: False
              legacy_entries:
                description:
                  - Legacy entries
                type: str
                required: False
              headers:
                description:
                  - headers
                type: str
                required: False
              selector:
                description:
                  - seclecor
                type: str
                required: False
          jms_topic:
            description:
              - Configure jms topic.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the jms topic.
                type: str
                required: True
              entries:
                description:
                  - Enter the required entries.
                type: list
                elements: str
                required: True
              legacy_entries:
                description:
                  - Legacy entries
                type: str
                required: False
              headers:
                description:
                  - headers
                type: str
                required: False
          connection_factory:
            description:
              - Configure connection factory.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the connection factory
                type: str
                required: True
              entries:
                description:
                  - Enter the required entries
                type: list
                elements: str
                required: True
              connectors:
                description:
                  - Legacy entries
                type: list
                elements: str
                required: False
              discovery_group:
                description:
                  - discovery group
                type: str
                required: False
          connector:
            description:
              - Configure connector.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the connector.
                type: str
                required: True
              factory_class:
                description:
                  - factory class
                type: str
                required: True
          bridge:
            description:
              - Configure bridge
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the bridge
                type: str
                required: True
              static_connectors:
                description:
                  - static connectors
                type: str
                required: True
              queue_name:
                description:
                  - queue name
                type: str
                required: True
              discovery_group:
                description:
                  - discovery group
                type: str
                required: True
          address_setting:
            description:
              - Configure address setting
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Enter the details of address setting.
                type: str
                required: True
              dead_letter_address:
                description:
                  - Sets the dead-letter-address.
                type: str
                required: False
              expiry_address:
                description:
                  - Sets the expiry-address.
                type: str
                required: False
              redelivery_delay:
                description:
                  - Sets the redelivery-delay.
                type: int
                required: False
              max_delivery_attempts:
                description:
                  - Sets max number of delivery attempts.
                type: int
                required: False
          security_setting:
            description:
              - Configure security setting
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Logical name of the bridge
                type: str
                required: True
              send:
                description:
                  - enter details to send
                type: str
                required: True
              consume:
                description:
                  - Consume
                type: str
                required: False
              create_non_durable_queue:
                description:
                  - create_non_durable_queue
                type: str
                required: False
              delete_non_durable_queue:
                description:
                  - delete_non_durable_queue
                type: str
                required: False
              manage:
                description:
                  - manage
                type: str
                required: False
              create_durable_queue:
                description:
                  - create_durable_queue
                type: str
                required: False
              delete_durable_queue:
                description:
                  - delete_durable_queue
                type: str
                required: False
          remote_acceptor:
            description:
              - Configure remote acceptor
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Enter the details of remote acceptor.
                type: str
                required: True
          remote_connector:
            description:
              - Configure remote connector
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Enter the details of remote acceptor.
                type: str
                required: True
              socket_binding:
                description:
                  - Enter the details of socket binding.
                type: str
                required: True
          in_vm_acceptor:
            description:
              - Configure in vm acceptor
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Enter the details of in vm acceptor.
                type: str
                required: True
              server_id:
                description:
                  - Enter the details of server id.
                type: str
                required: True
          pooled_connection_factory:
            description:
              - Configure pooled connection factory
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - Enter the details of pooled connection factory.
                type: str
                required: True
              connector:
                description:
                  - Enter the details of connector.
                type: str
                required: True
              entries:
                description:
                  - Enter entries.
                type: list
                elements: str
                required: True
              discovery:
                description:
                  - Enter the details of discovery.
                type: str
                required: False
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
    jcliff_command_line = ["bash", "-x",
                           data["jcliff"], "--cli=" +
                           data['wfly_home'] + "/bin/jboss-cli.sh",
                           "--ruledir=" + data['rules_dir'],
                           "--timeout=" + str(data['timeout']),
                           "--reconnect-delay=" + str(data['reconnect_delay']),
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
        reconnect_delay=dict(required=False, type='int', default=30000),
        components=dict(type='list', aliases=['subsystems'], required=False, elements='dict',
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
                                    password=dict(type='str', required=False, no_log=True),
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
                            xadatasources=dict(
                                type='list', required=False, elements='dict',
                                options=dict(
                                    name=dict(type='str', required=True),
                                    pool_name=dict(type='str', required=False),
                                    jndi_name=dict(type='str', required=True),
                                    use_java_context=dict(
                                        type='str', default='true'),
                                    xa_datasource_properties=dict(
                                        type='dict', required=True, options=dict(
                                          url=dict(type='str', required=False)
                                        )),
                                    driver_name=dict(
                                        type='str', required=True),
                                    enabled=dict(type='str', default='true'),
                                    password=dict(type='str', required=False),
                                    user_name=dict(type='str', required=False),
                                    no_recovery=dict(
                                        type='bool', default='undefined'),
                                    validate_on_match=dict(type='str', default='undefined'),
                                    background_validation=dict(
                                        type='bool', default='undefined'),
                                    valid_connection_checker_class_name=dict(
                                        type='str', default='undefined'),
                                    exception_sorter_class_name=dict(
                                        type='str', default='undefined'),
                                    check_valid_connection_sql=dict(
                                        type='str', default='undefined'),
                                    same_rm_override=dict(type='bool', default='undefined'),
                                    background_validation_millis=dict(type='int', default='undefined'),
                                    )),
                            system_properties=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=False),
                                    value=dict(type='str', required=False))),
                            deployments=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=True),
                                    path=dict(type='str', required=True),
                                    disabled=dict(type='bool', required=False),
                                    runtime_name=dict(type='str', required=False),
                                    replace_name_regex=dict(type='str', required=False),
                                    replace_runtime_name_regex=dict(type='str', required=False),
                                    unmanaged=dict(type='bool', required=False))),
                            interfaces=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=True),
                                    any_address=dict(type='bool', required=False),
                                    inet_address=dict(type='str', required=False),
                                    link_local_address=dict(type='bool', required=False),
                                    loopback=dict(type='bool', required=False),
                                    loopback_address=dict(type='str', required=False),
                                    multicast=dict(type='bool', required=False),
                                    nic=dict(type='str', required=False),
                                    nic_match=dict(type='str', required=False),
                                    point_to_point=dict(type='bool', required=False),
                                    public_address=dict(type='bool', required=False),
                                    resolved_address=dict(type='str', required=False),
                                    site_local_address=dict(type='bool', required=False),
                                    subnet_match=dict(type='str', required=False),
                                    up=dict(type='bool', required=False),
                                    virtual=dict(type='bool', required=False))),
                            logging=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=True),
                                    level=dict(type='str', required=False))),
                            mail=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=True),
                                    from_email=dict(type='str', required=True),
                                    jndi_name=dict(type='str', required=True),
                                    outbound_socket_binding_ref=dict(type='str', required=True),
                                    ssl=dict(type='bool', required=False))),
                            modcluster=dict(
                                type='dict', required=False, options=dict(
                                    proxy=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            listener=dict(type='str', required=False),
                                            advertise=dict(type='bool', required=False),
                                            advertise_security_key=dict(type='str', required=False, no_log=True),
                                            advertise_socket=dict(type='str', required=False),
                                            auto_enable_contexts=dict(type='bool', required=False),
                                            balancer=dict(type='str', required=False),
                                            excluded_contexts=dict(type='str', required=False),
                                            flush_packets=dict(type='bool', required=False),
                                            flush_wait=dict(type='int', required=False),
                                            load_balancing_group=dict(type='str', required=False),
                                            max_attempts=dict(type='int', required=False),
                                            node_timeout=dict(type='int', required=False),
                                            ping=dict(type='int', required=False),
                                            proxies=dict(type='list', required=False, elements='str'),
                                            proxy_list=dict(type='str', required=False),
                                            proxy_url=dict(type='str', required=False),
                                            session_draining_strategy=dict(type='str', required=False),
                                            simple_load_provider=dict(type='int', required=False),
                                            smax=dict(type='int', required=False),
                                            socket_timeout=dict(type='int', required=False),
                                            ssl_context=dict(type='str', required=False),
                                            status_interval=dict(type='int', required=False),
                                            sticky_session=dict(type='bool', required=False),
                                            sticky_session_force=dict(type='bool', required=False),
                                            sticky_session_remove=dict(type='bool', required=False),
                                            stop_context_timeout=dict(type='int', required=False),
                                            ttl=dict(type='int', required=False),
                                            worker_timeout=dict(type='int', required=False),
                                        )))),
                            scanner=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=False),
                                    value=dict(type='str', required=False))),
                            transactions=dict(
                                type='list', required=False, elements='dict', options=dict(
                                    name=dict(type='str', required=True),
                                    value=dict(type='str', required=True))),
                            standard_sockets=dict(
                                type='dict', required=False, options=dict(
                                    socket_binding=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            port=dict(type='str', required=True),
                                            interface=dict(type='str', required=False),
                                            multicast_address=dict(type='str', required=False),
                                            multicast_port=dict(type='str', required=False),
                                        )),
                                    remote_destination_outbound_socket_binding=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            host=dict(type='str', required=True),
                                            port=dict(type='int', required=True),
                                            fixed_source_port=dict(type='bool', required=False),
                                            source_interface=dict(type='str', required=False),
                                            source_port=dict(type='int', required=False),
                                        )))),
                            messaging_activemq=dict(
                                type='dict', required=False, options=dict(
                                    server_property=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            value=dict(type='str', required=True))),
                                    jms_queue=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            entries=dict(type='list', required=True, elements='str'),
                                            durable=dict(type='str', required=False),
                                            legacy_entries=dict(type='str', required=False),
                                            headers=dict(type='str', required=False),
                                            selector=dict(type='str', required=False),
                                        )),
                                    jms_topic=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            entries=dict(type='list', required=True, elements='str'),
                                            legacy_entries=dict(type='str', required=False),
                                            headers=dict(type='str', required=False),
                                        )),
                                    connection_factory=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            entries=dict(type='list', required=True, elements='str'),
                                            connectors=dict(type='list', required=False, elements='str'),
                                            discovery_group=dict(type='str', required=False),
                                        )),
                                    connector=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            factory_class=dict(type='str', required=True),
                                        )),
                                    bridge=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            static_connectors=dict(type='str', required=True),
                                            queue_name=dict(type='str', required=True),
                                            discovery_group=dict(type='str', required=True),
                                        )),
                                    address_setting=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            dead_letter_address=dict(type='str', required=False),
                                            expiry_address=dict(type='str', required=False),
                                            redelivery_delay=dict(type='int', required=False),
                                            max_delivery_attempts=dict(type='int', required=False)
                                        )),
                                    security_setting=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            send=dict(type='str', required=True),
                                            consume=dict(type='str', required=False),
                                            create_non_durable_queue=dict(type='str', required=False),
                                            delete_non_durable_queue=dict(type='str', required=False),
                                            manage=dict(type='str', required=False),
                                            create_durable_queue=dict(type='str', required=False),
                                            delete_durable_queue=dict(type='str', required=False),
                                        )),
                                    remote_acceptor=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                        )),
                                    remote_connector=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            socket_binding=dict(type='str', required=True),
                                        )),
                                    in_vm_acceptor=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            server_id=dict(type='str', required=True),
                                        )),
                                    pooled_connection_factory=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            name=dict(type='str', required=True),
                                            connector=dict(type='str', required=True),
                                            entries=dict(type='list', required=True, elements='str'),
                                            discovery=dict(type='str', required=False),
                                        )))),
                            keycloak=dict(
                                no_log=True, type='list', required=False, elements='dict', options=dict(
                                    secure_deployment=dict(
                                        type='list', required=False, elements='dict', options=dict(
                                            deployment_name=dict(type='str', required=True),
                                            realm=dict(type='str', required=False),
                                            auth_server_url=dict(type='str', required=True),
                                            ssl_required=dict(type='str', required=False),
                                            resource=dict(type='str', required=True),
                                            verify_token_audience=dict(type='bool', required=False),
                                            credential=dict(type='str', required=False),
                                            use_resource_role_mappings=dict(type='bool', required=False),
                                            disable_trust_manager=dict(type='bool', required=False),
                                        )))))),
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
