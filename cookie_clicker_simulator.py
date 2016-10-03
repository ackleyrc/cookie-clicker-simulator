"""
Cookie Clicker Simulator
"""

import math

import cookie_clicker_building_info as cc_buildinfo

# Constants
INITIAL_TIME = 0.0
SIM_TIME = 10000000.0
INITIAL_COOKIES = 0.0
INITIAL_CPS = 1.0

class ClickerState:
    """
    Simple class to keep track of the game state.
    """

    def __init__(self):
        self._total_cookies = INITIAL_COOKIES
        self._current_cookies = INITIAL_COOKIES
        self._current_time = INITIAL_TIME
        self._current_cps = INITIAL_CPS
        self._history = [(self._current_time,
                         None,
                         0.0,
                         self._total_cookies)]

    def __str__(self):
        """
        Returns human readable state
        """

        str_current_time = "Current time: " + str(self._current_time)
        str_current_cookies = "Current cookies: " + str(self._current_cookies)
        str_current_cps = "Current CPS: " + str(self._current_cps)
        str_total_cookies = "Total cookies produced: " + str(self._total_cookies)

        str_return = [str_current_time,
                     str_current_cookies,
                     str_current_cps,
                     str_total_cookies]

        return '\n'.join([string for string in str_return])

    def get_cookies(self):
        """
        Return current number of cookies
        (not total number of cookies)

        Returns a float
        """
        return self._current_cookies

    def get_cps(self):
        """
        Get current CPS (Cookies Per Second)

        Returns a float
        """
        return self._current_cps

    def get_time(self):
        """
        Get current time

        Returns a float
        """
        return self._current_time

    def get_history(self):
        """
        Return history list

        History list is a list of tuples of the form:
        (time, item, cost of item, total cookies)

        For example: [(0.0, None, 0.0, 0.0)]

        Returns a copy of the internal data structure,
        so that it will not be modified outside of the class.
        """
        return list(self._history)

    def time_until(self, cookies):
        """
        Return time until you have the given number of cookies
        (could be 0.0 if you already have enough cookies)

        Returns a float with no fractional part
        """

        if self._current_cookies >= cookies:
            return 0.0
        else:
            return math.ceil((cookies - self._current_cookies) / self._current_cps)

    def wait(self, time):
        """
        Wait for given amount of time and update state

        Does nothing if time <= 0.0
        """
        if time <= 0.0:
            return
        else:
            self._current_time += time
            new_cookies = time * self._current_cps
            self._current_cookies += new_cookies
            self._total_cookies += new_cookies

    def buy_item(self, item_name, cost, additional_cps):
        """
        Buy an item and update state

        Does nothing if you cannot afford the item
        """
        if self._current_cookies < cost:
            return
        else:
            self._current_cookies -= cost
            self._current_cps += additional_cps
            new_history_entry = (self._current_time,
                                 item_name,
                                 cost,
                                 self._total_cookies)
            self._history.append(new_history_entry)


def simulate_clicker(build_info, duration, strategy):
    """
    Function to run a Cookie Clicker game for the given
    duration with the given strategy.  Returns a ClickerState
    object corresponding to the final state of the game.
    """

    builds = build_info.clone()
    simulation = ClickerState()

    while simulation.get_time() <= duration:

        cookies = simulation.get_cookies()
        cps = simulation.get_cps()
        history = simulation.get_history()
        time_left = duration - simulation.get_time()
        selected_item = strategy(cookies, cps, history, time_left, builds)

        if selected_item == None:
            break
        else:
            cookies_needed = builds.get_cost(selected_item)
            wait_time = simulation.time_until(cookies_needed)
            if wait_time > time_left:
                break
            simulation.wait(wait_time)
            added_cps = builds.get_cps(selected_item)
            simulation.buy_item(selected_item, cookies_needed, added_cps)
            builds.update_item(selected_item)

    time_left = duration - simulation.get_time()
    simulation.wait(time_left)

    return simulation

def strategy_none(cookies, cps, history, time_left, build_info):
    """
    Always return None

    This is a pointless strategy that will never buy anything...
    """
    return None

def strategy_cursor_broken(cookies, cps, history, time_left, build_info):
    """
    Always pick Cursor!

    Note that this simplistic strategy does not properly check whether
    it can actually buy a Cursor in the time left. The simulate_clicker
    function automatically precludes buying if you cannot afford the item.
    """
    return "Cursor"

def strategy_cheap(cookies, cps, history, time_left, build_info):
    """
    Always buy the cheapest item you can afford in the time left.
    """

    items = build_info.build_items()
    costs = [build_info.get_cost(item) for item in items]
    builds = sorted(zip(costs,items))

    earnable_cookies = cookies + time_left * cps

    if builds[0][0] > earnable_cookies:
        return None
    else:
        return builds[0][1]

def strategy_expensive(cookies, cps, history, time_left, build_info):
    """
    Always buy the most expensive item you can afford in the time left.
    """

    items = build_info.build_items()
    costs = [build_info.get_cost(item) for item in items]
    builds = sorted(zip(costs,items))

    earnable_cookies = cookies + time_left * cps

    if builds[0][0] > earnable_cookies:
        return None
    else:
        most_expensive = builds[0]
        for build in builds:
            if build[0] < earnable_cookies and build[0] > most_expensive[0]:
                most_expensive = build

    return most_expensive[1]

def strategy_optimized(cookies, cps, history, time_left, build_info):
    """
    An optimized strategy that chooses the item
    with the greatest CPS per unit price.
    """

    items = build_info.build_items()
    costs = [build_info.get_cost(item) for item in items]
    value = [build_info.get_cps(item) / build_info.get_cost(item) for item in items]
    builds = sorted(zip(costs, value, items))

    earnable_cookies = cookies + time_left * cps

    if builds[0][0] > earnable_cookies:
        return None
    else:
        best_value = builds[0]
        for build in builds:
            if build[0] < earnable_cookies and build[1] > best_value[1]:
                best_value = build

    return best_value[2]

def run_strategy(strategy_name, time, strategy):
    """
    Run a simulation for the given time with one strategy.
    """
    state = simulate_clicker(cc_buildinfo.BuildInfo(), time, strategy)
    print(":: " + str(strategy_name) + " ::\n" + str(state) + "\n")

    # Optionally, print the buy history
    #print("\n".join([str(item) for item in state.get_history()]) + "\n")

def run():
    """
    Run the simulator.
    """

    # Uncomment the strategies you wish to see implemented
    run_strategy("None", SIM_TIME, strategy_none)
    run_strategy("Cursor Only", SIM_TIME, strategy_cursor_broken)
    run_strategy("Cheapest", SIM_TIME, strategy_cheap)
    run_strategy("Most Expensive", SIM_TIME, strategy_expensive)
    run_strategy("Optimized", SIM_TIME, strategy_optimized)


run()
