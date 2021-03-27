# Airport-Security-Check-Simulation

## Objectives
Simulate a simplified airport security system at a busy airport. 

## Description
Two checkpoints, one is the ID/boarding-pass check, the other is personal scanning.
Passengers arrive according to a Poisson distribution. 
First, they go to the ID/boarding-pass check queue, where there are several servers who each have exponential service time.
Then, the passengers are assigned to the shortest of the several personal-check queues, where they go through the personal scanner (time is uniformly distributed).
After that, the passengers leave to the airport lounge.

## Requirement
- SimPy
- Random


