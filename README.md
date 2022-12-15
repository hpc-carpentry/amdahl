# "Black Box" Amdahl's Law Simulator

This Python module contains a pseudo-application that can be used as a black
box to reproduce Amdahl's Law. It does not do real calculations, nor any real
communication, so can easily be overloaded.

The application is installed as a Python module with a shell script wrapper.
The only requirements are a Message Passing Interface (MPI) library and the
MPI for Python module, [mpi4py].

## Background

Amdahl's Law posits that some unit of work comprises a proportion $p$ that
benefits from parallel resources, and a proportion $s$ that is constrained to
execute in serial. The theoretical maximum speedup achievable for such a
workload is

$$
S = \frac{1}{s + p/N}
$$

where $S$ is the speedup relative to performing all of the work in serial and
$N$ is the number of parallel workers. A plot of $S$ vs. $N$ ought to look like
this, for $p = 0.89$ (since $s = 1 - p = 0.11$):

```output
  5┬────────┼────────┼────────┼────────·────────┼────────┼────────┼────────┼────────*
   │                                  ·                                             │
   │                                 ·                                     *        │
   │                                ·                                               │
   │                               ·                              *                 │
   │                              ·                                                 │
   │                             ·                                                  │
   │                            ·                        *                          │
   │                           ·                                                    │
  4┼                          ·                                                     ┼
   │                         ·                  *                                   │
   │                        ·                                                       │
   │                       ·                                                        │
   │                      ·                                                         │
   │                     ·             *                                            │
S  │                    ·                                                           │
p  │                   ·                                                            │
e  │                  ·                                                             │
e 3┼                 ·        *                                                     ┼
d  │                ·                                                               │
u  │               ·                                                                │
p  │              ·                                                                 │
   │             ·                                                                  │
   │            ·    *                                                              |
   │           ·                                                                    │
   │          ·                                                                     │
   │         ·                                                                      │
  2┼        ·                                                                       ┼
   │       ·                                                                        │
   │      · *                                                                       │
   │     ·                                                                          │
   │    ·                                                                           │
   │   ·                                                                            │
   │  ·                                                                             │
   │ ·                                                                              │
   │·                                                                               │
  1*────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┼────────┤
   1        2        3        4        5        6        7        8        9       10
                                         Workers
```

"Ideal scaling" ($p = 1$) is represented by the dotted line, $S = N$.

This graph shows there is a speed limit for every workload, and diminishing
returns on throwing more parallel processors at a problem. It is worth running
a "scaling study" to assess how far away that speed limit might be for the
given task.

## Setup

An external requirement is a Message Passing Interface (MPI) library, such as
[OpenMPI] or [MPICH]. To check whether you have one installed, run

```shell
which mpirun
```

If the command returns a filesystem path, e.g. `/usr/bin/mpirun`, you're all
set! If not, contact an administrator or use your operating system's package
manager to install both the binaries and the development headers for either
OpenMPI or MPICH.

Once an MPI library is installed, you should be able to install the
[amdahl][PyPI] package and its dependencies using [pip]:

```shell
python3 -m pip install --user amdahl
```

## Usage

Once installed, you can run the program using

```shell
mpirun -np 2 amdahl
```

You should see something like the following output:

```output
Doing 30 seconds of 'work' on 2 processors, which should take 18 seconds
with 0.8 parallel proportion of the workload.

  Hello, World! I am process 0 of 2. I will do all the serial 'work' for 6 seconds.
  Hello, World! I am process 0 of 2. I will do parallel 'work' for 10 seconds.
  Hello, World! I am process 1 of 2. I will do parallel 'work' for 14 seconds.

Total execution time (according to rank 0): 16 seconds
```

<!-- links -->
[MPICH]:   https://www.mpich.org
[OpenMPI]: https://www.open-mpi.org
[PyPI]:    https://pypi.org/project/amdahl
[mpi4py]:  https://mpi4py.readthedocs.io/en/stable/index.html
[pip]:     https://pip.pypa.io/en/stable
