import sys
import os
import psutil
from goad.command.cmd import Command
import subprocess

from goad.goadpath import GoadPath
from goad.log import Log
from goad.utils import Utils


class LinuxCommand(Command):

    def is_in_path(self, bin_file):
        command = f'which {bin_file} >/dev/null'
        try:
            subprocess.run(command, shell=True, check=True)
            Log.success(f'{bin_file} found in PATH')
            return True
        except subprocess.CalledProcessError as e:
            Log.error(f'{bin_file} not found in PATH')
            return False

    def run_shell(self, command, path):
        try:
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(command)
            subprocess.run(command, cwd=path, shell=True)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")

    def run_command(self, command, path):
        result = None
        try:
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(command)
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout, shell=True)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
            return False
        return result.returncode == 0

    def check_vagrant(self):
        return self.is_in_path('vagrant')

    def check_vagrant_plugin(self, plugin_name):
        try:
            result = subprocess.run(['vagrant', 'plugin', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if plugin_name in result.stdout:
                Log.success(f'vagrant plugin {plugin_name} is installed')
                return True
            else:
                Log.error(f'Missing vagrant plugin {plugin_name}')
                return False
        except FileNotFoundError:
            Log.error("Vagrant is not installed or not found in PATH.")
            return False

    def check_gem(self, gem_name):
        try:
            result = subprocess.run(['gem', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if gem_name in result.stdout:
                Log.success(f'ruby gem {gem_name} is installed')
                return True
            else:
                Log.warning(f'ruby gem {gem_name} not installed')
                return False
        except FileNotFoundError:
            Log.error("Ruby or gem is not installed or not found in PATH.")
            return False

    def check_vmware(self):
        return self.is_in_path('vmrun')

    def check_virtualbox(self):
        return self.is_in_path('VBoxManage')

    def check_terraform(self):
        return self.is_in_path('terraform')

    def check_aws(self):
        return self.is_in_path('aws')

    def check_azure(self):
        return self.is_in_path('az')

    def check_rsync(self):
        return self.is_in_path('rsync')

    def check_ansible(self):
        return self.is_in_path('ansible-playbook')

    def check_ludus(self):
        return self.is_in_path('ludus')

    def check_disk(self, min_disk_gb=120):
        disk_usage = psutil.disk_usage('/')
        free_disk_gb = disk_usage.free / (1024 ** 3)  # Convert bytes to GB
        if free_disk_gb < min_disk_gb:
            Log.warning(f'not enought disk space, only {str(free_disk_gb)} Gb available')
            return False
        return True

    def check_ram(self, min_ram_gb=24):
        total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
        if total_ram_gb < min_ram_gb:
            Log.error('not enough ram on the system')
            return False
        return True

    def run_vagrant(self, args, path):
        result = None
        try:
            command = ['vagrant']
            command += args
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(' '.join(command))
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
        return result.returncode == 0

    def run_terraform(self, args, path):
        result = None
        try:
            command = ['terraform']
            command += args
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(' '.join(command))
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
        return result.returncode == 0

    def run_terraform_output(self, args, path):
        result = None
        try:
            command = ['terraform', 'output', '-raw']
            command += args
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(' '.join(command))
            result = subprocess.run(command, cwd=path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                                    )
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None

            return result.stdout
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
        return None

    def run_ludus(self, args, path, api_key):
        env = os.environ.copy()
        env["LUDUS_API_KEY"] = api_key
        result = None
        try:
            command = 'ludus '
            command += args
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(command)
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout, shell=True, env=env)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
        return result.returncode == 0

    def run_ludus_status(self, path, api_key, do_log=True):
        result = None
        env = os.environ.copy()
        env["LUDUS_API_KEY"] = api_key
        try:
            command = ['ludus', 'range', 'status', '--json']
            if do_log:
                Log.info('CWD: ' + Utils.get_relative_path(str(path)))
                Log.cmd(' '.join(command))
            result = subprocess.run(command, cwd=path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    env=env
                                    )
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None

            return result.stdout
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
        return None

    def get_ludus_version_output(self, api_key):
        env = os.environ.copy()
        env["LUDUS_API_KEY"] = api_key
        result = subprocess.run(
            ["ludus", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        return result.stdout

    def run_ansible(self, args, path):
        result = None
        try:
            command = 'ansible-playbook '
            command += args
            Log.info('CWD: ' + Utils.get_relative_path(str(path)))
            Log.cmd(command)
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout, shell=True)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
            return False
        return result.returncode == 0

    def run_docker_ansible(self, args, path, sudo):
        result = None
        try:
            ansible_command = 'ansible-playbook '
            ansible_command += args
            command = f"{sudo} docker run -ti --rm --network host -h goadansible -v {GoadPath.get_project_path()}:/goad -w /goad/ansible goadansible /bin/bash -c '{ansible_command}'"
            Log.cmd(command)
            result = subprocess.run(command, cwd=path, stderr=sys.stderr, stdout=sys.stdout, shell=True)
        except subprocess.CalledProcessError as e:
            Log.error(f"An error occurred while running the command: {e}")
            return False
        return result.returncode == 0

    def get_azure_account_output(self):
        result = subprocess.run(
            ["az", "account", "list", "--output", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        return result.stdout

    def scp(self, source, destination, ssh_key):
        # rsync = f'rsync -a --exclude-from='.gitignore' -e "ssh -o 'StrictHostKeyChecking no' -i $CURRENT_DIR/ad/$lab/providers/$provider/ssh_keys/ubuntu-jumpbox.pem" "$CURRENT_DIR/" goad@$public_ip:~/GOAD/'
        Log.info(f'Launch scp -r {source} -> {destination}')
        scp_command = f"scp -r -o 'StrictHostKeyChecking no' -i {ssh_key}"
        command = f'{scp_command} {source} {destination}'
        self.run_shell(command, source)

    def rsync(self, source, destination, ssh_key, exclude=True):
        # rsync = f'rsync -a --exclude-from='.gitignore' -e "ssh -o 'StrictHostKeyChecking no' -i $CURRENT_DIR/ad/$lab/providers/$provider/ssh_keys/ubuntu-jumpbox.pem" "$CURRENT_DIR/" goad@$public_ip:~/GOAD/'
        Log.info(f'Launch Rsync {source} -> {destination}')
        ssh_command = f"ssh -o 'StrictHostKeyChecking no' -i {ssh_key}"
        exclude_from = ''
        if exclude:
            exclude_from = '--exclude-from=".gitignore"'
        command = f'rsync -a {exclude_from} -e "{ssh_command}" {source} {destination}'
        self.run_shell(command, source)
