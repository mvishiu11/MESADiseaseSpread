
"""Agent definitions for virus‑X spread model."""

import mesa


class PersonAgent(mesa.Agent):
    """Represents a single person on the grid."""

    def __init__(
        self,
        model: mesa.Model,
        is_infected: bool = False,
        has_comorbidities: bool = False,
        moving_probability: float = 0.8,
    ):
        super().__init__(model)
        self.is_infected = is_infected
        self.has_comorbidities = has_comorbidities
        self.moving_probability = moving_probability
        self.newly_infected = False

    # ---------- behaviour ----------
    def move(self) -> None:
        """Move to a random Von‑Neumann neighbour with given probability."""
        if self.random.random() < self.moving_probability:
            neighbours = self.model.grid.get_neighborhood(
                self.pos, moore=False, include_center=False
            )
            new_pos = self.random.choice(neighbours)
            self.model.grid.move_agent(self, new_pos)

    def attempt_infection(self, base_prob: float) -> bool:
        """Attempt to infect this agent and return True on success."""
        if self.is_infected:
            return False
        p = min(base_prob + (0.25 if self.has_comorbidities else 0.0), 1.0)
        if self.random.random() < p:
            self.newly_infected = True
            return True
        return False

    def step(self) -> None:
        """Agent's turn: only movement; infection is handled at model level."""
        self.move()
