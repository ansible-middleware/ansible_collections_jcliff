#!powershell

# (c) 2020, Red Hat, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic

Function Check_If_Folder_Exists {
    Param(
        [Parameter(Mandatory=$true)][Ansible.Basic.AnsibleModule]$module,
        [Parameter(Mandatory=$true)][String]$key
    )

    $folder = $module.Params[$key]

    if (-not (Test-Path -LiteralPath $(Resolve-Path -LiteralPath $module.Params[$key]) -PathType Container)) {
        $module.FailJson("$key is invalid: $folder")
    }
}

Function JCliff_Present {
    Param (
        [Parameter(Mandatory=$true)][Ansible.Basic.AnsibleModule]$module
    )

    Execute_Rules_With_Jcliff $module

    $module.Result.data = $module.Params

}

Function JCliff_Absent {
    Param (
        [Parameter(Mandatory=$true)][Ansible.Basic.AnsibleModule]$module
    )

    $module.Result.absent = "not yet implemented"
    $module.Result.data = $module.Params

}

Function List_Rule_files {
    Param (
        [Parameter(Mandatory=$true)][String]$rules_dir
    )

    $rule_files = @()

    Get-ChildItem -LiteralPath $rules_dir -Filter *jcliff.yml | ForEach-Object {
        $rule_files += $_.fullname
    }

    return $rule_files
}

Function Execute_Rules_With_Jcliff {
    Param (
        [Parameter(Mandatory=$true)][Ansible.Basic.AnsibleModule]$module
    )

    $jboss_cli_path = Join-Path -Path $(Resolve-Path -LiteralPath $module.Params.wfly_home) -ChildPath "bin/jboss-cli.bat"

    $jcliff_command_line_args = @("--cli=$jboss_cli_path", "--ruledir=$(Resolve-Path -LiteralPath $module.Params.rules_dir)", "--controller=$($module.Params.management_host):$($module.Params.management_port)", "-v")

    if ($module.Params.management_username) {
        $jcliff_command_line_args += "--user=$($module.Params.management_username)"
    }

    if ($module.Params.management_password) {
        $jcliff_command_line_args += "--password=$($module.Params.management_password)"
    }

    $jcliff_command_line_args += List_Rule_files $(Resolve-Path -LiteralPath $module.Params.remote_rulesdir)

    $env:JAVA_HOME = Resolve-Path -LiteralPath $module.Params.jcliff_jvm
    $env:JBOSS_HOME = Resolve-Path -LiteralPath $module.Params.wfly_home
    $env:JCLIFF_HOME = Resolve-Path -LiteralPath $module.Params.jcliff_home

    $psi = New-object System.Diagnostics.ProcessStartInfo

    $psi.CreateNoWindow = $true
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.FileName = $module.Params.jcliff
    $psi.Arguments = $jcliff_command_line_args
    $psi.LoadUserProfile = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi

    [void]$process.Start()

    $output = $process.StandardOutput.ReadToEnd()
    $process.WaitForExit()

    $module.Result.rc = $process.ExitCode

    if ($process.ExitCode -eq 0) {
        if($output -like '*Server configuration changed: true*') {
            $module.Result.jcliff = $jcliff_command_line_args
            $module.Result.changed = $true

        } else {
            $module.Result.changed = $false
        }
        $module.Result.present = $output
    } else {
        $module.Result.jcliff_cli = "$(Resolve-Path -LiteralPath $module.Params.jcliff) $($jcliff_command_line_args)"
        $module.FailJson("Failed to execute jcliff module", $output)

    }
}


$default_jcliff_home = "/usr/share/jcliff"
$default_jcliff = "/usr/bin/jcliff"
$default_rules_dir = "/usr/share/jcliff/rules"

$spec = @{
    options = @{
        jcliff_home = @{ type = "str"; default = $default_jcliff_home }
        jcliff = @{ type = "str"; default = $default_jcliff }
        management_username = @{ type = "str"; }
        management_password = @{ type = "str"; no_log = $true }
        rules_dir = @{ type = "str"; default = $default_rules_dir  }
        wfly_home = @{ type = "str" ; required = $true ; aliases = @("jboss_home") }
        management_host = @{ type = "str" ; default = "localhost" }
        management_port = @{ type = "str" ; default = "9990" }
        jcliff_jvm = @{ type = "str" ; default = $env:JAVA_HOME  }
        rule_file = @{ type = "str" }
        remote_rulesdir = @{ type = "str" }
        debug_mode = @{ type = "bool"; default = $false }
        subsystems = @{ type = "list"; elements = "dict";
            options = @{
                drivers = @{ type = "list"; elements = "dict";
                    options = @{
                        driver_name = @{ type = "str"; required = $true}
                        driver_module_name = @{ type = "str"; required = $true}
                        driver_xa_datasource_class_name = @{ type = "str"; default = "undefined"}
                        driver_class_name = @{ type = "str"; default = "undefined"}
                        driver_datasource_class_name = @{ type = "str"; default = "undefined"}
                        module_slot = @{ type = "str"; default = "undefined"}
                    }
                }
                datasources = @{ type = "list"; elements = "dict";
                    options = @{
                        name = @{ type = "str"; required = $true }
                        pool_name = @{ type = "str" }
                        jndi_name = @{ type = "str" }
                        use_java_context = @{ type = "str"; default = "true" }
                        connection_url = @{ type = "str"; required = $true }
                        driver_name = @{ type = "str"; required = $true }
                        enabled = @{ type = "str"; default = "true" }
                        password = @{ type = "str" }
                        user_name = @{ type = "str" }
                        max_pool_size = @{ type = "str"; default = "undefined"}
                        min_pool_size = @{ type = "str"; default = "undefined"}
                        idle_timeout_minutes = @{ type = "str"; default = "undefined"}
                        query_timeout = @{ type = "str"; default = "undefined"}
                        check_valid_connection_sql = @{ type = "str"; default = "undefined"}
                        validate_on_match = @{ type = "str"; default = "undefined"}
                    }
                }
                deployments = @{ type = "list"; elements = "dict";
                    options = @{
                        name = @{ type = "str"; required = $true }
                        path = @{ type = "str"; required = $true }
                        disabled = @{ type = "bool" }
                        runtime_name = @{ type = "str" }
                        replace_name_regex = @{ type = "str" }
                        replace_runtime_name_regex = @{ type = "str" }
                        unmanaged = @{ type = "bool" }
                    }
                }
                keycloak = @{ type = "list"; elements = "dict";
                    options = @{
                        secure_deployment = @{ type = "list"; elements = "dict";
                            options = @{
                                deployment_name = @{ type = "str"; required = $true }
                                realm = @{ type = "str" }
                                auth_server_url = @{ type = "str"; required = $true }
                                ssl_required = @{ type = "str" }
                                resource = @{ type = "str"; required = $true }
                                verify_token_audience = @{ type = "bool" }
                                credential = @{ type = "str" }
                                use_resource_role_mappings = @{ type = "bool" }
                            }
                        }
                    }
                }
                system_props = @{ type = "list"; elements = "dict";
                    options = @{
                        name = @{ type = "str"}
                        value = @{ type = "str"}
                    }
                }
                logging = @{ type = "list"; required = $false ; elements = "dict";
                    options = @{
                        name = @{ type = "str" ; required = $true }
                        level = @{ type = "str"; required = $false }
                    }
               }
            }
        }
        state = @{ type = "str"; choices = "absent", "present"; default = "present"  }
    }
    supports_check_mode = $false
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

if (Test-Path -LiteralPath env:JCLIFF_HOME) {
    $module.Params.jcliff_home = $env:JCLIFF_HOME
}

if ($module.Params.jcliff -eq $default_jcliff) {
    $module.Params.jcliff =Join-Path -Path $module.Params.jcliff_home -ChildPath "jcliff.bat"
}

if ($module.Params.rules_dir -eq $default_rules_dir) {
    $module.Params.rules_dir = Join-Path -Path $module.Params.jcliff_home -ChildPath "rules"
}

Check_If_Folder_Exists $module "jcliff_home"
Check_If_Folder_Exists $module "wfly_home"

if (!$module.Params.jcliff_jvm) {
    Check_If_Folder_Exists $module "jcliff_jvm"
}

if ($module.Params.state -eq "present") {
    JCliff_Present $module
} elseif ($state -eq "absent") {
    JCliff_Absent $module
}

$module.ExitJson()
