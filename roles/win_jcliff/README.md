jcliff
=========

Installs [jcliff](https://github.com/bserdar/jcliff) to manage Wildfly/JBoss EAP instances

Requirements
------------

A valid Java runtime environment must be available for execution of the jcliff utility

Role Variables
--------------

The following are a set of key varaiables for the role:


| Variable | Description | Required | Defaults |
|:---------|:------------|:---------|:---------|
|`jcliff_package_name`| Name of the package | no | `jcliff` |
|`jcliff_program_name`| Name of the program to install | no | `jcliff` |
|`jcliff_homebrew_tap`| Name of the Homebrew tap | no | `redhat-cop/redhat-cop` |
|`jcliff_yum_baseurl`| Base URL for the RPM repository | `http://people.redhat.com/~rpelisse/jcliff.yum` | `` |
|`jcliff_standalone`| Whether to install the standalone application binary instead of a package | no | `false` |
|`jcliff_standalone_version`| The version of the standalone binary to install | no | `2.12.5` |
|`jcliff_standalone_archive`| Location of the standalone archive containing the binary | no | `https://github.com/bserdar/jcliff/releases/download/<version>/jcliff-<version>-dist.tar.gz` |
|`jcliff_standalone_root`| Location of where the utility will be installed | no | `/usr/share` |
|`jcliff_standalone_home_dir`| Home directory for the utility | no | `/usr/share` |
|`jcliff_standalone_binary_dir`| Location where the binary will be installed | no | `/usr/bin` |

Dependencies
------------

None

Example Playbook
----------------

The following is an example playbook that makes use of the role

```yaml
---
- hosts: ...
    collections:
      - middleware_automation.jcliff
    tasks:
      - name: Include Jcliff role for windows
        include_role:
          name: win-jcliff
```

License
-------

GPL2

Author Information
------------------

* [Andrew Block](https://github.com/sabre1041)
* [Romain Pelisse](https://github.com/rpelisse) 