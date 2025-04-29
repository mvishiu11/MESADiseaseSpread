
"""Core model for virus‑X spread."""

from __future__ import annotations
import mesa
from mesa.space import MultiGrid, PropertyLayer
from mesa.datacollection import DataCollector
from typing import Tuple

from agents import PersonAgent


class InfectiousDiseaseSpreadModel(mesa.Model):
    """Simulate spread of an epidemic on a 2‑D toroidal grid."""

    def __init__(
        self,
        population_size: int = 100,
        initial_infected: int = 5,
        population_comorbidities: int = 10,
        moving_prob: float = 0.8,
        width: int = 20,
        height: int = 20,
        seed: int | None = None,
    ):
        super().__init__(seed=seed)

        self.grid = MultiGrid(width, height, torus=True)
        self.moving_prob = moving_prob

        # Counters
        self.interaction_infections = 0
        self.location_infections = 0

        # Cell infection map: (x,y) -> {timer:int, prob:float}
        self.cell_infection_map: dict[Tuple[int, int],
                                      dict[str, float | int]] = {}

        # Decide initial infection / comorbidity status
        idxs = list(range(population_size))
        self.random.shuffle(idxs)
        infected_set = set(idxs[:initial_infected])
        comorbid_set = set(idxs[initial_infected: initial_infected
                                + population_comorbidities])

        # Create agents
        for i in range(population_size):
            agent = PersonAgent(
                model=self,
                is_infected=i in infected_set,
                has_comorbidities=i in comorbid_set,
                moving_probability=self.moving_prob,
            )
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))

        # Property layer for cell infection intensity
        self.infection_layer = PropertyLayer(
            name="infection", width=width, height=height, default_value=0.0
        )
        self.grid.add_property_layer(self.infection_layer)

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "Interaction": lambda m: m.interaction_infections,
                "Location": lambda m: m.location_infections,
            }
        )

    # ----------- helpers -----------
    def _mark_cell(self, pos: Tuple[int, int], prob: float) -> None:
        self.cell_infection_map[pos] = {"timer": 2, "prob": prob}
        self.infection_layer.set_cell(pos, prob)

    def _update_cell_timers(self) -> None:
        expired = []
        for pos, info in self.cell_infection_map.items():
            info["timer"] -= 1
            if info["timer"] <= 0:
                expired.append(pos)
        for pos in expired:
            del self.cell_infection_map[pos]
            self.infection_layer.set_cell(pos, 0.0)

    def _direct_interactions(self) -> None:
        for contents, _ in self.grid.coord_iter():
            infected = [a for a in contents if a.is_infected]
            healthy = [a for a in contents if not a.is_infected]
            if infected and healthy:
                for h in healthy:
                    if h.attempt_infection(0.5):
                        self.interaction_infections += 1

    def _location_infections(self) -> None:
        for agent in self.agents:
            if agent.is_infected or agent.newly_infected:
                continue
            data = self.cell_infection_map.get(agent.pos)
            if data and agent.attempt_infection(data["prob"]):
                self.location_infections += 1

    def _spread_to_locations(self) -> None:
        for agent in self.agents:
            if agent.is_infected:
                cx, cy = agent.pos
                self._mark_cell((cx, cy), 0.5)
                for nx, ny in self.grid.get_neighborhood(
                    (cx, cy), moore=False, include_center=False
                ):
                    self._mark_cell((nx, ny), 0.25)

    # ----------- core step -----------
    def step(self) -> None:
        # reset flags
        for a in self.agents:
            a.newly_infected = False

        # 1. agent activation
        self.agents.shuffle_do("step")

        # 2. interactions
        self._direct_interactions()

        # 3. update & create infected cells
        self._update_cell_timers()
        self._spread_to_locations()

        # 4. location‑based infections
        self._location_infections()

        # 5. finalise states
        for a in self.agents:
            if a.newly_infected:
                a.is_infected = True

        # 6. collect
        self.datacollector.collect(self)

        # 7. stopping criterion
        if all(a.is_infected for a in self.agents):
            self.running = False
