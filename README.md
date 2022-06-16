# What does this package do?

This python module contains a pseudo-application that can be used as a black
box to reproduce Amdahl's Law. It does not do real calculations, nor any real
communication, so can easily be overloaded.

The application is installed as a python module with a shell
script wrapper. The only requirement is MPI4PY.

## Background

Amdahl's law posits that some unit of work comprises a proportion $p$ that
benefits from parallel resources, and a proportion $s$ that is constrained to
execute in serial. The theoretical maximum speedup achievable for such a
workload is

$$
S = \frac{1}{s + p/N}
$$

where $S$ is the speedup relative to performing all of the work in serial and
$N$ is the number of parallel workers. A plot of $S$ vs. $N$ ought to look like
this, for $p = 0.89$ ($s = 1 - p = 0.11$):

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

"Ideal scaling" ($p = 1$) is would be the line $y = x$ (or $S = N$),
represented here by the dotted line.

This graph shows there is a speed limit for every workload, and diminishing
returns on throwing more parallel processors at a problem. It is worth running
a "scaling study" to assess how far away that speed limit might be for the
given task.
