#! /usr/bin/env python
#  coding=utf-8
"""This shows the use of ${accelerator_name} accelerator.

${example_description}

Please, set up your configuration file before running following example.

Read Apyfal documentation for more information: https://apyfal.readthedocs.io"""

if __name__ == "__main__":
    from apyfal import Accelerator, get_logger

    # Enable extra information for this demo by logging (Disabled by default)
    get_logger(True)

    # Run example
    print("1- Creating Accelerator...")
    with Accelerator(accelerator='${accelerator_id}') as myaccel:

        print("2- Creating and Initializing Instance...")
${example_script_start}

        print("3- Processing")
${example_script_process}
        print("   Processing completed with success")

        print("4- Stopping Accelerator...")
    print("   Accelerator stopped.")
