import random
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
        self.valid_waypoints = ['left','forward','right']
        self.valid_lights = ['red', 'green']
        self.valid_actions = [None, 'forward', 'left', 'right']
        self.Q = {}
        for waypoint in self.valid_waypoints:
            for light in self.valid_lights:
                for oncoming in self.valid_actions:
                    self.Q[(waypoint, light, oncoming)] = [ random.random(), random.random(), random.random(), random.random()]           
        
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.trial += 1
        

    def success(self):
        print "{} Success!".format(self.trial)
        print self.env.agent_states[self.env.primary_agent]

    def fail(self):
        print "{} Fail".format(self.trial)
        
    def abort(self):
        print "{} Abort".format(self.trial)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (self.next_waypoint, inputs['light'], inputs['oncoming'])

        # TODO: Select action according to your policy
        

        Qvalue = self.Q[self.state]
        best_value = max(Qvalue)
        best_index = Qvalue.index(best_value)
        action = self.valid_actions[best_index]

        # Execute action and get reward
        reward = self.env.act(self, action)
		
        # TODO: Learn policy based on state, action, reward
        gamma = 0.2
        alpha = 0.5

        inputs = self.env.sense(self)

        nextMax = max(self.Q[(self.planner.next_waypoint(), inputs['light'], inputs['oncoming'])])

        self.Q[self.state][best_index] = (1 - alpha) * best_value + (alpha * (reward + gamma * nextMax))

        
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
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
