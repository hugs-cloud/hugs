from datetime import datetime
import json
from pathlib import Path
import tempfile

from HUGS.Jobs import SSHConnect

# Load in the template
def data_watchdog():
    pass

def run_job(job_data):
    """ Set a job to run on a HPC service

        Args:
            job_data (dict): Dictionary containing data needed to run the job
            such as the run command, number of nodes, number of tasks etc

            TODO - improve this 
        Returns:
            None ? 
    """
    bc4_partitions = ['cpu_test', 'dcv', 'gpu', 'gpu_veryshort', 'hmem', 'serial', 'test', 'veryshort']

    name = job_data["name"]
    run_command = job_data["run_command"]
    partition = job_data["partition"]
    
    if partition not in bc4_partitions:
        raise ValueError(f"Invalid partition selected. Please select from one of the following :\n{bc4_partitions}")
    # Need to create a job script from the paramters
    n_nodes = job_data["n_nodes"]
    n_tasks_per_node = job_data["n_tasks_per_node"]
    n_cpus_per_task = job_data["n_cpus_per_task"]
    # This is in GB
    memory_req = job_data["memory_req"]
    job_duration = job_data["job_duration"]

    # TODO - in the future this can set whether we use BC4/CitC etc
    # service = job_data["service"]

    if not memory_req.endswith("G"):
        raise ValueError("Memory requirements must be in gigabytes and end with a G i.e. 16G")

    # Create a dated and named filename and path in the user's home dir
    date_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"run_job__{name}_{date_str}.sh"

    with open(filepath, 'w') as rsh:
        rsh.write(f"""#!/bin/bash
    #SBATCH --partition={"test"}
    #SBATCH --nodes={n_nodes}
    #SBATCH --ntasks-per-node={n_tasks_per_node}
    #SBATCH --cpus-per-task={n_cpus_per_task}
    #SBATCH --time={job_duration}
    #SBATCH --mem={memory_req}
    {run_command}
        """)

    sc = SSHConnect()
    sc.connect(username="wm19361", hostname="bc4login.acrc.bris.ac.uk")
    sc.


    

    # Now we need to connec to the HPC cluster and set the job running





    


    
