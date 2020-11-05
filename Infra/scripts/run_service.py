import os, sys
import subprocess
import yaml
from PyInquirer import prompt, Separator

CORE_SERVICES = [{
    'name': 'Sites Checker Service',
    'value': {
        'name': 'sites-checker-service',
        'service_build_directory': 'SitesCheckerService',
        'working_directory': '.'
    }
}]

INFRA_SERVICES = [{
    'name': 'Consul',
    'value': {
        'name': 'consul',
    },
}, {
    'name': 'PostgreSQL',
    'value': {
        'name': 'postgresql',
    },
}]


if __name__ == '__main__':

    last_commit_sha = ''
    os.environ["BUILD_VERSION"] = ''

    if not os.path.isfile('docker-compose.local.yml'):
        users = {
            'version': '3.7',
            'networks': {
                'sites-checker': {'name': 'sites-checker', 'driver': 'bridge'}
                }
            }
        with open('docker-compose.local.yml', 'w') as f:
            data = yaml.dump(users, f, sort_keys=False)

    try:
        questions = [
            {
                'type': 'list',
                'name': 'mode',
                'message': 'Choose mode',
                'choices': ['Debug'],
            },
            {
                'type': 'list',
                'name': 'service',
                'message': 'Choose service',
                'choices': [*CORE_SERVICES, Separator(), *INFRA_SERVICES],
            },
            {
                'type': 'list',
                'name': 'action',
                'message': 'Choose action',
                'choices': [
                    'Start use cache',
                    'Start no cache (pull new image)',
                    'Stop', 'Restart'
                    ],
            },
        ]
        answers = prompt(questions)
        if not answers:
            sys.exit(0)
        mode = answers['mode']
        service_folder = answers['service'].get('service_build_directory')
        working_dir = answers['service'].get('working_directory')
        service_name = answers['service'].get('name')
        scale = answers['service'].get('scale', 1)
        commands = []
        if mode == 'Prod':
            if answers['action'] == 'Start no cache (pull new image)':
                commands.append([
                    'docker-compose',
                    '-f', 'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    'pull', service_name
                ])
                commands.append([
                    'docker-compose',
                    '-f', 'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    '-f', 'docker-compose.local.yml',
                    'up', '-d', '--scale',
                    f'{service_name}={scale}', service_name
                ])

            if answers['action'] == 'Start use cache':
                commands.append([
                    'docker-compose', '-f',
                    'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    '-f', 'docker-compose.local.yml',
                    'up', '-d', '--scale',
                    f'{service_name}={scale}', service_name
                ])

        else:
            if service_folder and working_dir:
                git_command = subprocess.run(
                    ['git', 'log', '-1',
                     '--pretty=format:%h',
                     '--', f"./{service_folder}/."],
                    stdout=subprocess.PIPE,
                    cwd=working_dir
                    )

                last_commit_sha = git_command.stdout.decode('utf-8')

                os.environ["BUILD_VERSION"] = last_commit_sha

            if answers['action'] == 'Start no cache (pull new image)':
                commands.append([
                    'docker-compose',
                    '-f', 'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    '-f', 'docker-compose.dev.yml',
                    'build', '--no-cache', service_name
                    ])
                commands.append([
                    'docker-compose',
                    '-f', 'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    '-f', 'docker-compose.dev.yml',
                    '-f', 'docker-compose.local.yml',
                    'up', '-d', '--build', '--scale',
                    f'{service_name}={scale}', service_name
                    ])

            if answers['action'] == 'Start use cache':
                commands.append([
                    'docker-compose',
                    '-f', 'docker-compose.infra.yml',
                    '-f', 'docker-compose.prod.yml',
                    '-f', 'docker-compose.dev.yml',
                    '-f', 'docker-compose.local.yml',
                    'up', '-d', '--build', '--scale',
                    f'{service_name}={scale}', service_name
                    ])

        if answers['action'] == 'Restart':
            commands.append([
                'docker-compose',
                '-f', 'docker-compose.infra.yml',
                '-f', 'docker-compose.prod.yml',
                'restart', service_name
                ])

        if answers['action'] == 'Stop':
            commands.append([
                'docker-compose',
                '-f', 'docker-compose.infra.yml',
                '-f', 'docker-compose.prod.yml',
                'stop', service_name
                ])

        for command in commands:
            subprocess.run(command)


    except Exception as ex:
        sys.exit(1)

    finally:
        if os.getenv('BUILD_VERSION'):
            del os.environ['BUILD_VERSION']
