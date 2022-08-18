import time
import sys
import argparse
import json
import random

from mpi4py import MPI

"""
Gather timing data in order to plot speedup *S* vs. number of cores *N*,
which should follow Amdahl's Law:

           1
    S = -------
        s + p/N

where *s* is the serial proportion of the total work,
      *p* the parallelizable proportion, and
      *s* + *p* == 1.
"""


def do_work(work_time=30,
            parallel_proportion=0.8,
            jitter_proportion=0.2,
            comm=MPI.COMM_WORLD,
            terse=False,
            exact=False):
    # How many MPI ranks (cores) are we?
    num_mpi_ranks = comm.Get_size()
    # Who am I in that set of ranks?
    rank = comm.Get_rank()
    # Where am I running?
    hostname = MPI.Get_processor_name()

    if rank == 0:
        # Ensure the work_time and parallel_proportion are floats, not integers
        work_time = float(work_time)
        parallel_proportion = float(parallel_proportion)

        # Derive the serial proportion from the parallel work proportion
        serial_proportion = 1 - parallel_proportion

        # Set the sleep times (which are used to fake the amount of work)
        serial_sleep_time = work_time * serial_proportion
        parallel_sleep_time = work_time * parallel_proportion / num_mpi_ranks

        # Use Amdahl's law to calculate the expected speedup for this workload
        amdahl_speed_up = 1.0 / (
            serial_proportion + (parallel_proportion / num_mpi_ranks)
        )

        if not exact:
            serial_sleep_time = random_jitter(serial_sleep_time,
                                              jitter_proportion)

        if num_mpi_ranks == 1:
            suffix = ""
        else:
            suffix = "s"

        if not terse:
            sys.stdout.write(
                "Doing %f seconds of 'work' on %s processor%s,\n"
                " which should take %f seconds with %f parallel"
                " proportion of the workload.\n\n"
                % (
                    work_time,
                    num_mpi_ranks,
                    suffix,
                    work_time / amdahl_speed_up,
                    parallel_proportion,
                )
            )

            sys.stdout.write(
                "  Hello, World! I am process %d of %d on %s."
                " I will do all the serial 'work' for"
                " %f seconds.\n"
                % (
                    rank,
                    num_mpi_ranks,
                    hostname,
                    serial_sleep_time
                )
            )
        time.sleep(serial_sleep_time)
    else:
        parallel_sleep_time = None

    # Tell all processes how much work they need to do using a broadcast
    # ('bcast') from the root rank. The 'bcast' function contains an MPI
    # "barrier", a function that no rank can exit until all ranks have
    # called it. This means that although the non-root ranks call the 'do_work'
    # function before the root rank, they all have to wait until the root rank
    # reaches this line and broadcasts its data before they can proceed.
    parallel_sleep_time = comm.bcast(parallel_sleep_time, root=0)

    # Similarly, broadcast whether processes should print their status as they
    # work or silently complete their tasks.
    terse = comm.bcast(terse, root=0)

    if not exact:
        # Each rank applies its own random deviation to the amount of time
        # it sleeps, in order to more accurately simulate variance in workloads
        # observed in real applications.
        parallel_sleep_time = random_jitter(parallel_sleep_time,
                                            jitter_proportion)

    if not terse:
        # Announce to the world what you're about to do.
        sys.stdout.write(
            "  Hello, World! "
            "I am process %d of %d on %s. I will do parallel 'work' for "
            "%f seconds.\n"
            % (
                rank,
                num_mpi_ranks,
                hostname,
                parallel_sleep_time
            )
        )

    # This is where everyone pretends to do work (really we are just sleeping)
    time.sleep(parallel_sleep_time)

    if rank == 0:
        # This function returns a "dict" containing named values.
        return {
            'host': hostname,
            'nproc': num_mpi_ranks,
            'serial_work': serial_sleep_time,
            'parallel_work': parallel_sleep_time
        }


def random_jitter(value, scaling=0.2):
    """
    Randomly increase a value up to the specified scaling factor
    (use a negative argument to decrease the value instead)
    """
    # Make sure scaling is between -1 and +1
    if abs(scaling) > 1:
        sign = scaling / abs(scaling)
        sys.stdout.write(
            "Changing the value by {:.0f}% isn't jitter, "
            "that's an earthquake!\n"
            "Using {:.1f} instead...".format(
                100 * sign * scaling,
                sign * 0.2
            )
        )
        scaling = 0.2 * sign

    # random() returns a float between 0 and 1, scale it down
    jitter_proportion = scaling * random.random()

    return (1 + jitter_proportion) * value


def parse_command_line():
    # Initialize our argument parser
    parser = argparse.ArgumentParser()

    # Register available arguments and their default values
    parser.add_argument(
        "-p",
        "--parallel-proportion",
        nargs="?",
        const=0.8,
        type=float,
        default=0.8,
        help="Parallel proportion: a float between 0 and 1",
    )
    parser.add_argument(
        "-w",
        "--work-seconds",
        nargs="?",
        const=30,
        type=int,
        default=30,
        help="Total seconds of workload: an integer greater than 0",
    )
    parser.add_argument(
        "-t",
        "--terse",
        action='store_true',
        default=False,
        help="Format output as a machine-readable object for easier analysis",
    )
    parser.add_argument(
        "-e",
        "--exact",
        action='store_true',
        default=False,
        help="Exactly match requested timing by disabling random jitter",
    )
    parser.add_argument(
        "-j",
        "--jitter-proportion",
        nargs="?",
        const=0.2,
        type=float,
        default=0.2,
        help="Random jitter: a float between -1 and +1",
    )

    # Read arguments from command line
    args = parser.parse_args()
    if not args.work_seconds > 0:
        parser.print_help()
        MPI.COMM_WORLD.Abort(1)
        sys.exit(1)
    if args.parallel_proportion <= 0 or args.parallel_proportion > 1:
        parser.print_help()
        MPI.COMM_WORLD.Abort(1)
        sys.exit(1)
    if abs(args.jitter_proportion) > 1:
        parser.print_help()
        MPI.COMM_WORLD.Abort(1)
        sys.exit(1)

    return args


def amdahl():
    """Amdahl's Law illustrator (with fake work)"""
    # Start a clock to measure total time
    start = time.time()

    # Get the identity of this rank
    rank = MPI.COMM_WORLD.Get_rank()

    # Ensure that each parallel rank uses its own unique seed, else the
    # generated numbers will be identical sequences -- not random at all!
    random.seed(int(time.time()) + rank)

    # Only the root process reads the command line arguments.
    if rank == 0:
        args = parse_command_line()

    # Every MPI rank must call the do_work() function.
    if rank == 0:
        # The root rank supplies arguments to the function,
        # parsed from the command line.
        summary = do_work(
            work_time=args.work_seconds,
            parallel_proportion=args.parallel_proportion,
            jitter_proportion=args.jitter_proportion,
            terse=args.terse,
            exact=args.exact
        )
    else:
        # All other ranks start with default parameters, which will be
        # overwritten with values broadcast from the root rank.
        do_work()

    # Stop the clock
    end = time.time()

    # Only the root rank writes output to the terminal.
    if rank == 0:
        summary["parallel_proportion"] = args.parallel_proportion
        summary["execution_time"] = (end - start)

        if args.terse:
            sys.stdout.write(
                json.dumps(summary, indent=4) + "\n"
            )
        else:
            sys.stdout.write(
                "\nTotal execution time (according to rank 0): "
                "%f seconds\n" % summary["execution_time"]
            )
