from pprint import pprint

import matplotlib.pyplot as plt
import mesa
from mesa import Model


def compute_gini(model):
    print("GINI HERE")
    print("*"*100)
    agent_wealths = [agent.health for agent in model.agents]
    x = sorted(agent_wealths)
    n = model.num_agents
    B = sum(xi * (n - i) for i, xi in enumerate(x)) / (n * sum(x))
    return 1 + (1 / n) - 2 * B


class Axeman(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

        self.health = 200
        self.type = "B"
        self.base_attack = 100

    def attack(self):
        if self.health > 0:
            neighbors = self.model.grid.get_neighbors(pos=self.pos, moore=True, radius=2)
            if len(neighbors):
                other_agent = self.random.choice(neighbors)
                print("Axeman " + str(self.unique_id) + "Attacked Archer " + str(other_agent.unique_id))
                other_agent.health -= self.base_attack
                print("Archer "+ str(other_agent.unique_id) + " HP = "+ str(other_agent.health) )
                if other_agent.health <=0:
                    print("Removed Archer " + str(other_agent.unique_id))
                    other_agent.remove()
                    self.model.grid.remove_agent(other_agent)

            else:
                pass

    def move(self):
        closest_distance = float('inf')
        closest_a = None
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=False):
            if neighbor.type == "A":
                distance = abs(self.pos[0] - neighbor.pos[0]) + abs(self.pos[1] - neighbor.pos[1])
                # distance = mesa.space.Distance.euclidean_distance(self.pos, neighbor.pos)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_a = neighbor

        # Move one step towards the closest Agent A
        if closest_a:
            x_diff = closest_a.pos[0] - self.pos[0]
            y_diff = closest_a.pos[1] - self.pos[1]

            # Normalize the movement vector to ensure one-cell movement
            if abs(x_diff) >= abs(y_diff):
                x_move = 1 if x_diff > 0 else -1
                y_move = 0
            else:
                x_move = 0
                y_move = 1 if y_diff > 0 else -1

            new_pos = (self.pos[0] + x_move, self.pos[1] + y_move)
            self.model.grid.move_agent(self, new_pos)


class Archer(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        super().__init__(model)
        self.health = 100
        self.type = "A"
        # self.name = name
        self.base_attack = 25


    def attack(self):
        if self.health > 0:
            agent_bs = [i for i in self.model.agents if i.type == "B" ]
            if len(agent_bs):
                random_b = self.random.choice(agent_bs)
                distance = abs(self.pos[0] - random_b.pos[0]) + abs(self.pos[1] - random_b.pos[1])
                # distance = mesa.space.Distance.euclidean_distance(self.pos, random_b.pos)
                if distance !=0:
                    attack_power = self.base_attack/distance
                else:
                    attack_power = 5
                random_b.health -= attack_power
                print("Archer "+ str(self.unique_id) + " attacked Axeman " + str(random_b.unique_id) + " HP "+ str(random_b.health))
                if random_b.health <= 0:
                    random_b.remove()
                    print("Removed Axeman " + str(random_b.unique_id))
                    self.model.grid.remove_agent(random_b)


            else:
                print("No Axemen Left")
    def move(self):
        pass



class MyModel(Model):
    def __init__(self, width, height, num_agents_A, num_agents_B):
        super().__init__(seed=100)
        self.grid = mesa.space.MultiGrid(width, height, False)
        # self.datacollector = mesa.DataCollector(
        #     model_reporters={agent_reporters={"HP": "health"})

        self.data = mesa.DataCollector(
            model_reporters={"Gini": 1}, agent_reporters={"health": "health"}
        )

        for i in range(num_agents_A):
            a = Archer( self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(num_agents_B):
            b = Axeman( self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(b, (x, y))

    def step(self):
        self.agents.shuffle_do("move")
        self.agents.shuffle_do("attack")



model = MyModel(10, 1, 2,2)
num_archers = []
num_axemen = []
for i in range(10):
    print("Step : ",i)
    num_archers.append(len([agent.unique_id for agent in model.agents if agent.type == "A"]))
    num_axemen.append(len([agent.unique_id for agent in model.agents if agent.type == "B"]))
    model.step()
plt.plot(range(10), num_archers, label="Archers", color="dodgerblue", linewidth=2, marker="o", markersize=4)
plt.plot(range(10), num_axemen, label="Axemen", color="orange", linewidth=2, marker="s", markersize=4)
plt.legend(fontsize=12, loc="upper left", shadow=True, fancybox=True)

# Add gridlines
plt.grid(color='gray', linewidth=0.5, alpha=0.7)
plt.show()

# if __name__ == "__main__":
#     Step = 10
#     archers = 10
#     axeman = 10
#     h = 10
#     w = 10
#     archer_hp = 100
#     axeman_hp = 200
#     archer_damage = 30
#