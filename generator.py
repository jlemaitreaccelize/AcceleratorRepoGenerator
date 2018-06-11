#! /usr/bin/env python
#  coding=utf-8
"""This script generate or update Accelerator Git repository"""
import argparse
from collections import OrderedDict
from string import Template
from os import listdir
from os.path import join, abspath, dirname

import xmltodict


class Generator:
    """Accelerator Repository generator

    Args:
        dest_path (str): Destination path
        accelerator_def (str): Path to accelerator definition XML file.
    """
    # Templates directory
    TEMPLATE_DIR = join(abspath(dirname(__file__)), 'template')

    # Command line arguments mapping
    COMMAND_ARGS = {
        'datafile': '-i',
        'file_out': '-o',
        'file_in': '-i',
        'specific': '-j'}

    COMMAND_MODES = {
        'start': 0,
        'process': 1,
        'stop': 2}

    # If parameter before, add separator
    APYFAL_SEP = {'file_out': {'file_in'},
                  'start_specific': {'datafile'},
                  'process_specific': {'file_in', 'file_out'}}

    def __init__(self, dest_path, accelerator_def):
        self._identifiers = {}
        self._dest_path = dest_path

        with open(accelerator_def, 'rb') as xml:
            # Read XML file as dict
            self._accelerator_def = xmltodict.parse(xml)['repository']

    def _get_template_identifiers(self):
        """Read XML identifiers"""
        template = self._accelerator_def['template']
        for key in template:
            value = template[key]
            self._identifiers[key] = value if value else ''

    @staticmethod
    def _describe_parameter(parameter_node, param=''):
        """Return formated line describing a parameter.

        Args:
            parameter_node (dict): Dict with parameter description
            param (str): Parameter.

        Returns:
            str: Parameter description line.
        """
        desc = parameter_node['desc']
        if not desc:
            return ""
        values = parameter_node.get('value')

        if not param:
            param = parameter_node.get('@name')

        # Values list
        if values:
            value_text = ' Possibles values:\n%s' % '\n'.join([
                '    * `%s`: %s' % (value['value'], value['desc'].rstrip('.'))
                for value in values])
        else:
            value_text = ''

        return '* `%s`: %s.%s' % (
            param, desc.rstrip('.'), value_text)

    def _generate_specific_paragraph(self, specifics, title):
        """Format a "specific" section.

        Args:
            specifics (dict or list): <specific> content.
            title (str): Title of section.
        Returns:
            str: formated specific
        """
        if not specifics:
            return ''

        if isinstance(specifics, dict):
            # Convert single dict to list of dicts
            specifics = [specifics]

        # List specifics
        formatted_specifics = [
            self._describe_parameter(specific)
            for specific in specifics]

        # Add title and convert as str
        formatted_specifics.insert(0, '**%s:**' % title)
        return '\n'.join(formatted_specifics)

    def _generate_parameters_paragraphs(self):
        """Generate parameter description"""
        parameters = self._accelerator_def['parameters']

        for section in parameters:
            method = parameters[section]
            if not method:
                self._identifiers['parameters_%s' % section] = ''
                continue

            # Generate parameters description
            base_parameters = []
            specific_parameters = ''
            for key in method:
                # Specific parameters
                if key == 'specific':
                    specific_parameters = self._generate_specific_paragraph(
                        method[key], 'Specific parameters')
                    continue

                # Base parameters
                if method[key]:
                    desc = self._describe_parameter(method[key], key)
                    if desc:
                        base_parameters.append(desc)

            # Generate paragraph
            paragraph = []
            if base_parameters:
                base_parameters.insert(0, '**Generic parameters:**')
                paragraph.append('\n'.join(base_parameters))

            if specific_parameters:
                paragraph.append(specific_parameters)

            self._identifiers['parameters_%s' % section] = '\n\n'.join(paragraph)

        # Process output
        output = self._accelerator_def['output']
        output_desc = []
        if output:
            if output.get('desc'):
                # Use custom description
                output_desc.append('%s.' % output.get('desc').strip("."))

            if output.get('@file_out', '').lower() == 'true':
                try:
                    has_file_out = parameters['process']['file_out']['desc']
                except (KeyError, TypeError):
                    has_file_out = False

                if has_file_out:
                    output_desc.append(
                        'Processing output is file defined by `file_out` parameter.')

            specific_outputs = self._generate_specific_paragraph(
                    output.get('specific'), 'Specific outputs')
            if specific_outputs:
                output_desc.append(specific_outputs)

        self._identifiers['process_output'] = '\n\n'.join(output_desc)

    def _read_call(self, call, method):
        """"""
        if call is None:
            call = dict()

        accelerator_command = []
        apyfal_command = []

        # Get call description
        desc = call.pop('desc', None)
        if desc:
            desc = '%s.' % desc.rstrip('.')
            apyfal_command.append('    #    %s' % desc)
            accelerator_command.append(desc)

        # Get specific output
        output = call.pop('specific_output', None)

        # Get parameters
        generic_params = OrderedDict()
        specific_params = OrderedDict()

        for key in call:
            if key == 'specific':
                specifics = call[key]
                if not isinstance(specifics, list):
                    specifics = [specifics]
                for specific in specifics:
                    specific_params[specific['@name']] = specific['#text']
            else:
                generic_params[key] = call[key]

        # Generate Apyfal command:
        all_parameters = generic_params.copy()
        all_parameters.update(specific_params)
        apyfal_parameters = ', '.join([
            '%s=%s' % (key, all_parameters[key])
            for key in all_parameters])

        if output:
            # Get specific result
            result_variable = 'result = '
            result_key = '["%s"]' % output
        else:
            result_variable = ''
            result_key = ''

        apyfal_command.append('    %smyaccel.%s(%s)%s' % (
            result_variable, method, apyfal_parameters, result_key))

        # Generate command line accelerator argument

        if specific_params:
            # Add JSON to parameters line
            generic_params['specific'] = 'parameters.json'

            # Generate JSON description
            accelerator_command.append(
                    'With `parameters.json` as:\n```python\n'
                    '{"app": {"specific": {%s}}}\n```' % (', '.join([
                        '"%s": %s' %
                        (key, specific_params[key])
                        for key in specific_params])))

        accelerator_command.append(
            "```bash\nsudo /opt/accelize/accelerator/accelerator %s %s\n```" % (
                '-m %d' % self.COMMAND_MODES[method],
                ' '.join(['%s %s' % (self.COMMAND_ARGS[param], generic_params[param])
                    for param in generic_params])))

        return '\n'.join(apyfal_command), '\n'.join(accelerator_command)

    def _generate_example(self):
        """Generate identifiers used in examples"""
        # TODO: Multi "process" or "start" call with different parameters
        # Reads sequence and generate commands
        example = self._accelerator_def['example']

        apyfal_commands = []
        accelerator_commands = []
        output = {}

        def insert_command(info, call):
            """Insert commands in lists

            Args:
                info (dict): Information
                call (str): method called"""
            commands = self._read_call(info, call)
            try:
                output['file_out'] = info['file_out']
            except (KeyError, TypeError):
                pass
            apyfal_commands.append(commands[0])
            accelerator_commands.append(commands[1])

        for call in example:
            call_info = example[call]
            if isinstance(call_info, list):
                for info in call_info:
                    insert_command(info, call)
            else:
                insert_command(call_info, call)

        # Get starts commands
        self._identifiers["example_apyfal_start"] = apyfal_commands[0]
        self._identifiers["example_accelerator_start"] = accelerator_commands[0]

        # Get Process commands
        self._identifiers["example_apyfal_process"] = '\n'.join(apyfal_commands[1:])
        self._identifiers["example_accelerator_process"] = '\n\n'.join(accelerator_commands[1:])

        # Generate example script commands:
        for key in ('start', 'process'):
            commands = self._identifiers["example_apyfal_%s" % key].splitlines()
            commands_script = []
            for command in commands:
                if '#' not in command:
                    commands_script.append('    %s' % command)
            self._identifiers["example_script_%s" % key] = '\n'.join(commands_script)

        # Output
        if 'file_out' in output:
            self._identifiers['example_output'] = ">The result is the `%s` file.\n" % output['file_out']
        else:
            self._identifiers['example_output'] = ''

    def _create_from_template(self):
        """Generate files from template."""
        for file in listdir(self.TEMPLATE_DIR):
            # Read template
            with open(join(self.TEMPLATE_DIR, file), 'rt') as template_file:
                template = Template(template_file.read())

            # Perform substitution
            result = template.safe_substitute(self._identifiers)

            # Write result
            with open(join(self._dest_path, file), 'wt') as result_file:
                result_file.write(result)

    def generate(self):
        """Generate Repository files"""
        self._get_template_identifiers()
        self._generate_example()
        self._generate_parameters_paragraphs()
        self._create_from_template()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate or update Accelerator repository files. '
        'Require a file ".resources/accelerator_def.xml" in repository path.')
    parser.add_argument('--path', default='.',
                        help='Path to the repository directory.')
    args = parser.parse_args()

    repository = abspath(args.path)
    xml_path = join(repository, '.resources/accelerator_def.xml')
    Generator(dest_path=repository, accelerator_def=xml_path).generate()
