
"""Solara front‑end for virus‑X spread model (Mesa 3.1+)."""

from mesa.visualization import (SolaraViz,
                                make_space_component,
                                make_plot_component)

from disease_spread.model import InfectiousDiseaseSpreadModel
from disease_spread.agents import PersonAgent


# --------------- portrayal ---------------
def agent_portrayal(agent: PersonAgent):
    return {
        "color": "red" if agent.is_infected else "green",
        "marker": "s" if agent.has_comorbidities else "o",
        "size": 20,
    }


# --------------- build viz page ---------------
def build_page():
    model_params = {
        "population_size": {
            "type": "SliderInt",
            "label": "Population size",
            "value": 100,
            "min": 10,
            "max": 400,
            "step": 10,
        },
        "initial_infected": {
            "type": "SliderInt",
            "label": "Initially infected",
            "value": 5,
            "min": 1,
            "max": 100,
            "step": 1,
        },
        "population_comorbidities": {
            "type": "SliderInt",
            "label": "Comorbidities",
            "value": 10,
            "min": 0,
            "max": 100,
            "step": 1,
        },
        "moving_prob": {
            "type": "SliderFloat",
            "label": "Movement probability",
            "value": 0.8,
            "min": 0.0,
            "max": 1.0,
            "step": 0.05,
        },
        "width": 20,
        "height": 20,
    }

    model = InfectiousDiseaseSpreadModel(
        population_size=model_params["population_size"]["value"],
        initial_infected=model_params["initial_infected"]["value"],
        population_comorbidities=model_params["population_comorbidities"]["value"],
        moving_prob=model_params["moving_prob"]["value"],
        width=model_params["width"],
        height=model_params["height"],
    )

    Space = make_space_component(agent_portrayal)
    Plot = make_plot_component(["Interaction", "Location"])

    viz = SolaraViz(
        model,
        components=[Space, Plot],
        model_params=model_params,
        name="Virus‑X Spread Simulation",
    )
    return viz


page = build_page()
