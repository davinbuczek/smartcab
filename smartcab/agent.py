import random
import csv
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.trial = 0
        self.steps = 0
        self.deadline = 0
        self.alpha = 0.5
        self.gamma = 0.2
        self.data_list = [["Trial", "Status", "Deadline", "Steps"]] # lists of lists for capturing data from trial rums for performance tuning
        self.valid_waypoints = ['left','forward','right'] # list of valid directions based on suggested waypoint
        self.valid_lights = ['red', 'green'] # list of valid traffic light states
        self.valid_actions = [None, 'forward', 'left', 'right'] # list of valid actions the smartcab can take
        self.Q = {} # initialize Q dictionary for chosen evniornment states to random values
        for waypoint in self.valid_waypoints:
            for light in self.valid_lights:
                for oncoming in self.valid_actions:
                    self.Q[(waypoint, light, oncoming)] = [ random.random(), random.random(), random.random(), random.random()]           
        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.deadline = self.env.agent_states[self.env.primary_agent]['deadline']
        self.steps = 0
        self.trial += 1
        
    def summary(self, status):
        self.data_list.append([self.trial, status, self.deadline, self.steps])

        if self.trial == 100: # once test complete write data_list struct to csv file
            filename = "alpha{}_gamma{}.csv".format(self.alpha, self.gamma)
            with open(filename, 'wb') as csvfile:
                writer = csv.writer(csvfile, dialect='excel')
                writer.writerows(self.data_list)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'])
        self.steps += 1

        # TODO: Select action according to your policy
        Qvalue = self.Q[self.state] # assign Qvalue to current state
        best_value = max(Qvalue) # assign best_value to the max value of Qvalue
        best_index = Qvalue.index(best_value) # assign best_index to the index of the best_value
        action = self.valid_actions[best_index] # assign action to the value of best index

        # Execute action and get reward
        reward = self.env.act(self, action)
		
        # TODO: Learn policy based on state, action, reward

        inputs = self.env.sense(self)

        nextMax = max(self.Q[(self.planner.next_waypoint(), inputs['light'], inputs['oncoming'])])

        self.Q[self.state][best_index] = (1 - self.alpha) * best_value + (self.alpha * (reward + self.gamma * nextMax))

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}"\
        #.format(deadline, inputs, action, reward)  # [debug]

	def return_state(self):
		return self.state

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
