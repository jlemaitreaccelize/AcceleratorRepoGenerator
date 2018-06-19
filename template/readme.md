${accelerator_badges}

# ${accelerator_name}

${accelerator_description}

## Features

${accelerator_features}
- Remote or local execution facility
- Easy to use Python API

## Limitations

${accelerator_limitations}
- Inputs and outputs can't be larger than 30GB.
- See also limitations from API

## Parameters

This section describes accelerator inputs and outputs.

### Configuration parameters
${parameters_start}

### Processing parameters
${parameters_process}

### Processing output
${process_output}

## Getting started

The [Apyfal](https://apyfal.readthedocs.io) Python library is required.

Apyfal installation is made with PIP. Some installation options are available depending the host you want to use (See 
["Installation" in Apyfal documentation](https://apyfal.readthedocs.io/en/latest/installation.html)
for more information).

You can install the full package with all options using:

```bash
pip install apyfal[all]
```

### Using Accelerator with Apyfal

#### Running example

${example_description}

You can clone repository to get examples files, then move to the cloned directory:

```bash
git clone ${accelerator_git_base}${accelerator_git} --depth 1
cd ${accelerator_git}
```

You need to create and configure an `accelerator.conf` file to run example.
See ["Configuration" in Apyfal documentation](https://apyfal.readthedocs.io/en/latest/configuration.html)
for more information.

You can run the previously explained example of use with Apyfal :
```bash
./run_example.py
```
${example_output}
${example_extra_end_text}

### Using Apyfal step to step

This section only explain the use of this particular accelerator. For explanation on Apyfal use and host configuration,
See ["Getting Started" in Apyfal documentation](https://apyfal.readthedocs.io/en/latest/getting_started.html).

```python
import apyfal

# 1- Create Accelerator
with apyfal.Accelerator(accelerator='${accelerator_id}') as myaccel:
    
    # 2- Configure Accelerator and its host
    #    Note: This step can take some minutes depending the configured host
${example_apyfal_start}
    
    # 3- Process file
${example_apyfal_process}
```
${example_output}

### Local execution on cloud instance

This section show how to perform the above example directly with low-level accelerator command.

This example requires an host running the accelerator.

#### Creating cloud instance host using Apyfal

You can easily generate a Cloud instance host with Apyfal (See previous section for more information):

```python
import apyfal

with apyfal.Accelerator(accelerator='${accelerator_id}') as myaccel:
    # Use "keep" stop_mode to not automatically terminate host instance
    myaccel.start(stop_mode='keep')

    # Get host IP address (Required to remote access to the instance)
    host_ip = myaccel.host.public_ip

    # Get host instance ID (Required to terminate instance)
    instance_id = myaccel.host.instance_id
    
    # Get host key pair
    key_pair = myaccel.host.key_pair
```

And then connect to it with SSH:

```bash
ssh -Yt -i ${key_pair} centos@${host_ip}
```

#### Accelerator configuration

Like previously, first configure the accelerator. This performs the equivalent of  the Apyfal `start` method.

${example_accelerator_start}

#### Process with accelerator

Then, process with accelerator.

${example_accelerator_process}
${example_output}

#### Terminate cloud instance
Don't forget to terminate instance you have created with Apyfal once you have finished with it:

> Previously saved `instance_id` is used to take control on instance.
> `stop_mode` is set to `term` to delete instance.

```python
import apyfal

apyfal.Accelerator(accelerator='${accelerator_id}', instance_id='instance_id').stop(stop_mode='term')
```

## Support and enhancement requests

[Contact us](https://accelstore.accelize.com/contact-us/) if you have any support or enhancement request
