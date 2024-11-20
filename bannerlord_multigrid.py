import mesa
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from mesa.time import SimultaneousActivation


class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, model):
        super().__init__(model)
        self.health = 100
        self.attack_points = 30

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def attack(self):
        if self.health > 0:
            neighbors = self.model.grid.get_neighbors(pos=self.pos, moore=True, radius=1)
            if len(neighbors):
                other_agent = self.random.choice(neighbors)
                other_agent.health -= self.attack_points
                if other_agent.health <0:
                    other_agent.remove()

class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, n, width, height, seed=None):
        super().__init__(seed=seed)
        self.num_agents = n
        self.grid = mesa.space.MultiGrid(width, height, True)
        # self.schedule = SimultaneousActivation(self)

        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.agents.shuffle_do("move")
        self.agents.shuffle_do("attack")

    def get_health_grid(self):
        health_grid = [[0 for _ in range(self.grid.width)] for _ in range(self.grid.height)]

        for cell in self.grid.coord_iter():
            cell_contents, pos = cell
            if cell_contents:
                x,y = pos
                # print(pos,agent_health)
                # Average health of agents in the cell
                total_health = sum(agent.health for agent in cell_contents)
                health_grid[y][x] = total_health / len(cell_contents)

        return health_grid

model = MoneyModel(100, 10, 10)
for _ in range(20):
    model.step()
agent_health = model.get_health_grid()
heatmap_data = [[cell if cell is not None else 0 for cell in row] for row in agent_health]

# Visualize the heatmap
plt.figure(figsize=(8, 6))
plt.imshow(heatmap_data, cmap='hot', interpolation='nearest')
plt.colorbar(label="Health")
plt.title("Final Health of Agents")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.show()
# agent_counts = np.zeros((model.grid.width, model.grid.height))
# for cell_content, (x, y) in model.grid.coord_iter():
#     agent_count = len(cell_content)
#     agent_counts[x][y] = agent_count
# # Plot using seaborn, with a visual size of 5x5
# g = sns.heatmap(agent_counts, cmap="viridis", annot=True, cbar=False, square=True)
# g.figure.set_size_inches(5, 5)
# g.set(title="number of agents on each cell of the grid");
# plt.show()