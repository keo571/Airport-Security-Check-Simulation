import simpy
import random


class AirportSecurityCheck(object):
    """An airport security system has a limited number of ID/boarding-pass check servers (``NUM_CHECKERS``) and
    personal scanners (``NUM_SCANNERS``) to check arrived passengers in parallel.

    Passengers have to request one of the checkers and scanners. When they got one, they can start the processes
    and wait for it to finish."""

    def __init__(self, env, num_checkers, num_scanners):
        self.env = env
        self.checkers = simpy.Resource(env, num_checkers)
        self.scanners = []

        """Each scanner has its own queue."""
        for i in range(0, num_scanners):
            resource = simpy.Resource(env, capacity=1)
            self.scanners.append(resource)

    def check(self, passenger):
        """The ID/boarding-pass check process. It takes a ``passenger`` process and tries to serve him/her."""
        yield self.env.timeout(random.expovariate(1 / CHECK_RATE))
        # print("%s is under the ID/boarding-pass check." % (passenger))

    def scan(self, passenger):
        """The personal check processes. It takes a ``passenger`` processes and tries to scan him/her."""
        yield self.env.timeout(random.uniform(0.5, 1))
        # print("%s is under the personal check." % (passenger))


def passenger(env, name, cz):
    """Passenger arrives at the check zone (``cz``). First he/she requests a ID/boarding-pass check. The serving
    process starts. Passenger waits for it to finish.

    Then passenger requests a personal scan. The scanning process starts. Passenger also waits for it to finish.
    After that, passenger leaves to airport lounge ... """

    global check_wait
    global scan_wait
    global total_wait
    global totThrough

    arrive_time = env.now
    # print('%s arrives at the check zone at %.2f and request a ID/boarding-pass check.' % (name, arrive_time))

    with cz.checkers.request() as request:
        yield request
        # print('There are %d people before %s in the ID/boarding-pass check queue.' % (len(cz.server.queue), name))

        check_start = env.now
        # print('%s begins the ID/boarding-pass check at %.2f.' % (name, check_start))

        yield env.process(cz.check(name))

        check_complete = env.now
        # print('%s finishes the ID/boarding-pass check at %.2f and requests the personal check.' % (name,
        # check_complete))

    """Then the passengers are assigned to the shortest of the several personal-check queues."""
    shortest_q = 0
    for i in range(1, NUM_SCANNERS):
        if len(cz.scanners[i].queue) < len(cz.scanners[shortest_q].queue):
            shortest_q = i

    with cz.scanners[shortest_q].request() as request:
        yield request
        # print('There are %d people before %s in the personal check queue.' % (len(cz.scanners[shortest_q].queue),
        # name))

        scan_start = env.now
        # print('%s begins the personal check at %.2f.' % (name, scan_start))

        yield env.process(cz.scan(name))

        scan_complete = env.now
        # print('%s finishes the personal check at %.2f. and leaves to airport lounge.' % (name, scan_complete))

    check_wait = check_wait + (check_start - arrive_time)
    scan_wait = scan_wait + (scan_start - check_complete)
    total_wait = check_wait + scan_wait

    """Count passenger who got through the system."""
    totThrough += 1


def setup(env, num_checkers, num_scanners, arr_rate):
    """Create an airport security system and generate passengers according to a simple Poisson process."""
    passengers = 0

    """Create the airport security system."""
    security_check = AirportSecurityCheck(env, num_checkers, num_scanners)

    """Infinite loop for generating passengers according to a poisson process."""
    while True:
        passengers += 1

        """Generate next inter-arrival time"""
        iat = random.expovariate(arr_rate)

        """Register the processes with the simulation environment"""
        env.process(passenger(env, 'Passenger %d' % passengers, security_check))

        """Yield to a 'timeout' event and resume after iat time units."""
        yield env.timeout(iat)


if __name__ == '__main__':

    RANDOM_SEED = 123
    NUM_CHECKERS = 35  # Number of the ID/boarding-pass checkers
    NUM_SCANNERS = 35  # Number of personal scanners

    CHECK_RATE = 0.75  # ID/boarding-pass check rate (minutes per passenger)
    ARR_RATE = 50  # Arrival rate (passengers per minute)
    SIM_TIME = 720  # Simulation time in minutes
    REPS = 20  # Run simulation n times

    """Store simulation results"""
    avg_total_wait = []
    avg_check_wait = []
    avg_scan_wait = []

    """Run the simulation for REPS times"""
    for i in range(0, REPS):
        """Create an environment and start the setup process."""
        env = simpy.Environment()

        """Initiate global variables."""
        check_wait = 0
        scan_wait = 0
        total_wait = 0
        totThrough = 0

        """Execute"""
        env.process(setup(env, NUM_CHECKERS, NUM_SCANNERS, ARR_RATE))
        env.run(until=SIM_TIME)

        """Store average times for this REP"""
        avg_total_wait.append(total_wait / totThrough)
        avg_check_wait.append(check_wait / totThrough)
        avg_scan_wait.append(scan_wait / totThrough)

    """Result"""
    sim_total_wait = sum(avg_total_wait) / REPS
    sim_check_wait = sum(avg_check_wait) / REPS
    sim_scan_wait = sum(avg_scan_wait) / REPS

    print('Average total wait: ' + str(sim_total_wait))
    print('Average check wait: ' + str(sim_check_wait))
    print('Average scan wait: ' + str(sim_scan_wait))
