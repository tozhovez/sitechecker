import sys
import subprocess
from PyInquirer import prompt, Separator
from run_service import CORE_SERVICES, INFRA_SERVICES


if __name__ == '__main__':

    try:
        questions = [
            {
                'type': 'checkbox',
                'name': 'service',
                'message': 'Choose service',
                'choices': [*CORE_SERVICES, Separator(), *INFRA_SERVICES],
            }
        ]

        answers = prompt(questions)

        if not answers:
            sys.exit(0)

        command = ['docker-compose',
                   '-f', 'docker-compose.infra.yml',
                   '-f', 'docker-compose.dev.yml',
                   'pull']
        for service in answers['service']:
            service_name = service.get('name')
            command.append(service_name)
        # process = subprocess.Popen(command,
        #                                stdout=subprocess.PIPE,
        #                                stderr=subprocess.PIPE)
        # stdout, stderr = process.communicate()
        subprocess.run(command)

    except Exception as ex:
        sys.exit(1)
