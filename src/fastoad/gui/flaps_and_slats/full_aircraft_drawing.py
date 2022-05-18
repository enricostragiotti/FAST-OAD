#  This file is part of FAST-OAD : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2021 ONERA & ISAE-SUPAERO
#  FAST is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from ipywidgets import widgets, HBox
from IPython.display import display


from fastoad.io import VariableIO

COLS = plotly.colors.DEFAULT_PLOTLY_COLORS
NACELLE_POSITION = 0.6  # Nacelle position compared to the leading edge. 0 means that the back of the nacelle is aligned with the beginning of the root, 1 means that the beginning of the nacelle is aligned with the kink_x.
HORIZONTAL_TAIL_ROOT = 0.3  # Percentage of the tail root concerned by the elevator
HORIZONTAL_TAIL_TIP = 0.3  # Percentage of the tail tip, at 90 percent of the horizontal tail width, covered by the elevator


def full_aircraft_drawing_plot(
    aircraft_file_path: str, name=None, fig=None, file_formatter=None
) -> go.FigureWidget:
    """
    Returns a figure plot of the top view of the aircraft with the engines, the flaps, the slats and the elevator.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :return: wing plot figure
    """
    variables = VariableIO(aircraft_file_path, file_formatter).read()

    # Wing parameters
    wing_kink_leading_edge_x = variables["data:geometry:wing:kink:leading_edge:x:local"].value[0]
    wing_tip_leading_edge_x = variables["data:geometry:wing:tip:leading_edge:x:local"].value[0]
    wing_root_y = variables["data:geometry:wing:root:y"].value[0]
    wing_kink_y = variables["data:geometry:wing:kink:y"].value[0]
    wing_tip_y = variables["data:geometry:wing:tip:y"].value[0]
    wing_root_chord = variables["data:geometry:wing:root:chord"].value[0]
    wing_kink_chord = variables["data:geometry:wing:kink:chord"].value[0]
    wing_tip_chord = variables["data:geometry:wing:tip:chord"].value[0]
    nacelle_diameter = variables["data:geometry:propulsion:nacelle:diameter"].value[0]
    nacelle_length = variables["data:geometry:propulsion:nacelle:length"].value[0]
    nacelle_y = variables["data:geometry:propulsion:nacelle:y"].value[0]

    trailing_edge_kink_sweep_100_outer = variables["data:geometry:wing:sweep_100_outer"].value[0]
    slat_chord_ratio = variables["data:geometry:slat:chord_ratio"].value[0]
    slat_span_ratio = variables["data:geometry:slat:span_ratio"].value[0]
    total_wing_span = variables["data:geometry:wing:span"].value[0]
    flaps_span_ratio = variables["data:geometry:flap:span_ratio"].value[0]
    flaps_chord_ratio = variables["data:geometry:flap:chord_ratio"].value[0]
    mean_aerodynamic_chord = variables["data:geometry:wing:MAC:length"].value[0]
    mac25_x_position = variables["data:geometry:wing:MAC:at25percent:x"].value[0]
    distance_root_mac_chords = variables["data:geometry:wing:MAC:leading_edge:x:local"].value[0]

    # Wing
    y_wing = np.array(
        [0, wing_root_y, wing_kink_y, wing_tip_y, wing_tip_y, wing_kink_y, wing_root_y, 0, 0]
    )

    x_wing = np.array(
        [
            0,
            0,
            wing_kink_leading_edge_x,
            wing_tip_leading_edge_x,
            wing_tip_leading_edge_x + wing_tip_chord,
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_root_chord,
            wing_root_chord,
            0,
        ]
    )

    # Engine
    y_engine = np.array(
        [
            nacelle_y - nacelle_diameter / 2,
            nacelle_y + nacelle_diameter / 2,
            nacelle_y + nacelle_diameter / 2,
            nacelle_y - nacelle_diameter / 2,
            nacelle_y - nacelle_diameter / 2,
        ]
    )
    x_engine = np.array([-nacelle_length, -nacelle_length, 0, 0, -nacelle_length])

    # Horizontal Tail parameters
    ht_root_chord = variables["data:geometry:horizontal_tail:root:chord"].value[0]
    ht_tip_chord = variables["data:geometry:horizontal_tail:tip:chord"].value[0]
    ht_span = variables["data:geometry:horizontal_tail:span"].value[0]
    ht_sweep_0 = variables["data:geometry:horizontal_tail:sweep_0"].value[0]
    ht_sweep_100 = variables["data:geometry:horizontal_tail:sweep_100"].value[0]

    ht_tip_leading_edge_x = ht_span / 2.0 * np.tan(ht_sweep_0 * np.pi / 180.0)

    y_ht = np.array([0, ht_span / 2.0, ht_span / 2.0, 0.0, 0.0])

    x_ht = np.array(
        [0, ht_tip_leading_edge_x, ht_tip_leading_edge_x + ht_tip_chord, ht_root_chord, 0]
    )

    # Fuselage parameters
    fuselage_max_width = variables["data:geometry:fuselage:maximum_width"].value[0]
    fuselage_length = variables["data:geometry:fuselage:length"].value[0]
    fuselage_front_length = variables["data:geometry:fuselage:front_length"].value[0]
    fuselage_rear_length = variables["data:geometry:fuselage:rear_length"].value[0]

    x_fuselage = np.array(
        [
            0.0,
            0.0,
            fuselage_front_length,
            fuselage_length - fuselage_rear_length,
            fuselage_length,
            fuselage_length,
        ]
    )

    y_fuselage = np.array(
        [
            0.0,
            fuselage_max_width / 4.0,
            fuselage_max_width / 2.0,
            fuselage_max_width / 2.0,
            fuselage_max_width / 4.0,
            0.0,
        ]
    )

    # Flaps
    # Part of the code dedicated to the flaps

    flap_chord_kink = wing_kink_chord * flaps_chord_ratio
    flap_chord_tip = wing_tip_chord * flaps_chord_ratio

    # Inboard flap
    # Part of the code dedicated to the inboard flap

    y2 = np.array([wing_kink_y, wing_kink_y, wing_root_y, wing_root_y, wing_kink_y])
    y2 = np.concatenate((-y2, y2))

    x2 = np.array(
        [
            wing_root_chord,
            wing_root_chord - flap_chord_kink,
            wing_root_chord - flap_chord_kink,
            wing_root_chord,
            wing_root_chord,
        ]
    )

    x2 = x2 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x2 = np.concatenate((x2, x2))

    # Outboard flap
    # Part of the code dedicated to the outboard flap

    # The points "_a" and "_b" are the ones placed on the trailing edge.
    # The points "_c" and "_d" are the projection of "_a" and "_b" normal to the trailing edge, on the wing.
    # This projection is made with a rotation matrix.
    # The points are place respecting the flaps span ratio compared to the total span of the aircraft.

    rotation_matrix = np.array(
        [
            [
                np.cos(trailing_edge_kink_sweep_100_outer * np.pi / 180),
                np.sin(trailing_edge_kink_sweep_100_outer * np.pi / 180),
            ],
            [
                -np.sin(trailing_edge_kink_sweep_100_outer * np.pi / 180),
                np.cos(trailing_edge_kink_sweep_100_outer * np.pi / 180),
            ],
        ]
    )

    y_a = wing_kink_y
    x_a = wing_root_chord

    y_b = wing_root_y + (total_wing_span / 2) * flaps_span_ratio
    x_b = (
        wing_tip_leading_edge_x
        + wing_tip_chord
        - (wing_tip_y - (wing_root_y + (total_wing_span / 2) * flaps_span_ratio))
        * np.tan(trailing_edge_kink_sweep_100_outer * np.pi / 180)
    )

    c_local = np.array([-flap_chord_tip, 0])
    x_c, y_c = rotation_matrix @ c_local + np.array([x_b, y_b])

    d_local = np.array([-flap_chord_kink, 0])
    x_d, y_d = rotation_matrix @ d_local + np.array([x_a, y_a])

    y3 = np.array([y_a, y_b, y_c, y_d, y_a])
    y3 = np.concatenate((-y3, y3))

    x3 = np.array([x_a, x_b, x_c, x_d, x_a])

    x3 = x3 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x3 = np.concatenate((x3, x3))

    # Design line
    # Part of the code dedicated to a lign only used for an aesthetic reason.
    # This line joins the two inboard flaps

    y4 = np.array([wing_root_y])
    y4 = np.concatenate((-y4, y4))

    x4 = np.array([wing_root_chord])

    x4 = x4 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x4 = np.concatenate((x4, x4))

    # Slats
    # Part of the code dedicated to the slats
    # The dimensions are given by two parameters : span_ratio and chord_ratio
    # Here the span_ratio is given by the span of the airplane minus the fuselage radius
    # the chord_ratio is given by the kink chord

    wing_span_no_fuselage = wing_tip_y - wing_root_y

    slat_y = (
        (1 - slat_span_ratio) / 2.0 * wing_span_no_fuselage
    )  # position in y of the beginning of the slats near the root
    slat_x_root = wing_tip_leading_edge_x * (1 - slat_span_ratio) / 2.0

    y5 = np.array(
        [
            slat_y + wing_root_y,
            slat_y + wing_root_y,
            wing_tip_y - slat_y,
            wing_tip_y - slat_y,
            slat_y + wing_root_y,
        ]
    )

    y6 = -y5  # slats on the other wing

    x5 = np.array(
        [
            slat_x_root,
            slat_x_root + slat_chord_ratio * wing_kink_chord,
            wing_tip_leading_edge_x * (1 - (1 - slat_span_ratio) / 2.0)
            + slat_chord_ratio * wing_kink_chord,
            wing_tip_leading_edge_x * (1 - (1 - slat_span_ratio) / 2.0),
            slat_x_root,
        ]
    )
    x5 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    x6 = x5

    # CGs
    wing_25mac_x = variables["data:geometry:wing:MAC:at25percent:x"].value[0]
    wing_mac_length = variables["data:geometry:wing:MAC:length"].value[0]
    local_wing_mac_le_x = variables["data:geometry:wing:MAC:leading_edge:x:local"].value[0]
    local_ht_25mac_x = variables["data:geometry:horizontal_tail:MAC:at25percent:x:local"].value[0]
    ht_distance_from_wing = variables[
        "data:geometry:horizontal_tail:MAC:at25percent:x:from_wingMAC25"
    ].value[0]

    x_wing = x_wing + wing_25mac_x - 0.25 * wing_mac_length - local_wing_mac_le_x
    x_engine += (
        wing_25mac_x
        - 0.25 * wing_mac_length
        - local_wing_mac_le_x
        + NACELLE_POSITION * nacelle_length
    )
    x_ht = x_ht + wing_25mac_x + ht_distance_from_wing - local_ht_25mac_x

    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x_fuselage, x_wing, x_ht))
    # pylint: disable=invalid-name # that's a common naming
    y = np.concatenate((y_fuselage, y_wing, y_ht))

    # pylint: disable=invalid-name # that's a common naming
    y = np.concatenate((-y, y))
    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x, x))

    # Design of the elevator
    A = x_fuselage[5] - x_ht[3]  # constants used for the computation

    B = y_fuselage[4] - y_fuselage[5]  # constants used for the computation

    D = x_ht[2] - x_ht[3]  # constants used for the computation

    E = y_ht[1] - y_ht[3]  # constants used for the computation

    tg_alpha = (y_fuselage[3] - y_fuselage[4]) / (
        x_fuselage[4] - x_fuselage[3]
    )  # constants used for the computation

    ht_root_tip_90_percent = (x_ht[2] - 0.1 * y_ht[1] * np.tan(ht_sweep_100 * np.pi / 180)) - (
        x_ht[1] - 0.1 * y_ht[1] * np.tan(ht_sweep_0 * np.pi / 180)
    )  # constants used for the computation. Root chord at 90 percent of the horizontal tail width

    delta_l = (ht_root_chord - np.tan(ht_sweep_0 * np.pi / 180) * (B + A * tg_alpha)) / (
        1 + np.tan(ht_sweep_0 * np.pi / 180) * tg_alpha
    )  # constants used for the computation

    delta_y_tot = tg_alpha * (A + delta_l)  # constants used for the computation

    delta_x = (A * E - D * B) / (E + D * tg_alpha)  # constants used for the computation

    delta_y = tg_alpha * delta_x  # constants used for the computation

    x_elevator = np.array(
        [
            x_fuselage[4] - delta_x,
            x_ht[3] - delta_l * HORIZONTAL_TAIL_ROOT,
            x_ht[2]
            - 0.1 * y_ht[1] * np.tan(ht_sweep_100 * np.pi / 180)
            - HORIZONTAL_TAIL_TIP * ht_root_tip_90_percent,
            x_ht[2] - 0.1 * y_ht[1] * np.tan(ht_sweep_100 * np.pi / 180),
            x_fuselage[4] - delta_x,
        ]
    )
    y_elevator = np.array(
        [
            y_fuselage[4] + delta_y,
            y_fuselage[4] + HORIZONTAL_TAIL_ROOT * delta_y_tot,
            y_ht[1] * 0.9,
            y_ht[1] * 0.9,
            y_fuselage[4] + delta_y,
        ]
    )

    if fig is None:
        fig = go.Figure()

    scatter_aircraft = go.Scatter(
        x=y, y=x, line=dict(color="blue"), mode="lines", name=name, showlegend=False
    )  # Aircraft
    scatter_left = go.Scatter(
        x=y_engine, y=x_engine, line=dict(color="blue"), mode="lines", name=name, showlegend=False
    )  # Left engine
    scatter_right = go.Scatter(
        x=-y_engine, y=x_engine, line=dict(color="blue"), mode="lines", name=name, showlegend=False
    )  # Right engine
    scatter2 = go.Scatter(
        x=y2,
        y=x2,
        mode="lines",
        line=dict(color="blue", width=1),
        name=name,
        showlegend=False,
    )  # first flap
    scatter3 = go.Scatter(
        x=y3,
        y=x3,
        mode="lines",
        line=dict(color="blue", width=1),
        name=name,
        showlegend=False,
    )  # second flap
    scatter4 = go.Scatter(
        x=y4, y=x4, mode="lines", line=dict(color="blue", width=1), name=name, showlegend=False
    )  # design line
    scatter5 = go.Scatter(
        x=y5,
        y=x5,
        line=dict(color="blue", width=1),
        mode="lines",
        name=name,
        showlegend=False,
    )  # slats
    scatter6 = go.Scatter(
        x=y6,
        y=x6,
        line=dict(color="blue", width=1),
        mode="lines",
        name=name,
        showlegend=False,
    )  # slats
    scatter_elevator_right = go.Scatter(
        x=y_elevator,
        y=x_elevator,
        line=dict(color="blue", width=1),
        mode="lines",
        name=name,
        showlegend=False,
    )
    scatter_elevator_left = go.Scatter(
        x=-y_elevator,
        y=x_elevator,
        line=dict(color="blue", width=1),
        mode="lines",
        name=name,
        showlegend=False,
    )  # elevator

    fig.add_trace(scatter_aircraft)
    fig.add_trace(scatter_right)
    fig.add_trace(scatter_left)
    fig.add_trace(scatter3)
    fig.add_trace(scatter2)
    fig.add_trace(scatter4)
    fig.add_trace(scatter5)
    fig.add_trace(scatter6)
    fig.add_trace(scatter_elevator_right)
    fig.add_trace(scatter_elevator_left)

    fig.layout = go.Layout(yaxis=dict(scaleanchor="x", scaleratio=1))

    fig = go.FigureWidget(fig)

    fig.update_layout(title_text="Aircraft Geometry", title_x=0.5, xaxis_title="y", yaxis_title="x")

    return fig

def wing_drawing_plot(
    aircraft_file_path: str, name=None, fig=None, file_formatter=None
) -> go.FigureWidget:
    """
    Returns a figure plot of the top view of the wing with the relevant distances on it.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :return: wing plot figure
    """
    variables = VariableIO(aircraft_file_path, file_formatter).read()

    wing_kink_leading_edge_x = variables["data:geometry:wing:kink:leading_edge:x:local"].value[0]
    wing_tip_leading_edge_x = variables["data:geometry:wing:tip:leading_edge:x:local"].value[0]
    wing_root_y = variables["data:geometry:wing:root:y"].value[0]
    wing_kink_y = variables["data:geometry:wing:kink:y"].value[0]
    wing_tip_y = variables["data:geometry:wing:tip:y"].value[0]
    wing_area = variables["data:geometry:wing:area"].value[0]
    wing_root_chord = variables["data:geometry:wing:root:chord"].value[0]
    wing_kink_chord = variables["data:geometry:wing:kink:chord"].value[0]
    wing_tip_chord = variables["data:geometry:wing:tip:chord"].value[0]
    trailing_edge_kink_sweep_100_outer = variables["data:geometry:wing:sweep_100_outer"].value[0]
    sweep_0 = variables["data:geometry:wing:sweep_0"].value[0]
    total_wing_span = variables["data:geometry:wing:span"].value[0]
    mean_aerodynamic_chord = variables["data:geometry:wing:MAC:length"].value[0]
    mean_aerodynamic_chord_y_global = variables["data:geometry:wing:MAC:y"].value[0]
    mac25_x_position = variables["data:geometry:wing:MAC:at25percent:x"].value[0]
    distance_root_mac_chords = variables["data:geometry:wing:MAC:leading_edge:x:local"].value[0]

    # 1) overall wing
    # Part of the code dedicated to the geometry of the general wing

    y = np.array(
        [wing_root_y, wing_kink_y, wing_tip_y, wing_tip_y, wing_kink_y, wing_root_y, wing_root_y]
    )

    x = np.array(
        [
            0,
            wing_kink_leading_edge_x,
            wing_tip_leading_edge_x,
            wing_tip_leading_edge_x + wing_tip_chord,
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_root_chord,
            0,
        ]
    )

    x = x + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x, x))

    # 2) flaps
    # Not represented here

    # 3) slats
    # Not represented here

    # 4) Fuselage axis
    # The line representing the fuselage axis in y=0
    y_fuselage = np.array([0, 0])
    x_fuselage = np.array([-wing_root_chord * 0.2, wing_root_chord * 1.6])
    x_fuselage += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 5) Tip (L3)
    # The line along the tip of the wing
    y_l3 = np.array([wing_tip_y * 1.03, wing_tip_y * 1.03])
    x_l3 = np.array([wing_tip_leading_edge_x, wing_tip_leading_edge_x + wing_tip_chord])
    x_l3 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 6) Leading edge to tip (X1)
    # The line parallel to the fuselage axis joining the leading edge and the tip
    y_x1 = np.array([wing_tip_y * 1.03, wing_tip_y * 1.03])
    x_x1 = np.array([0, wing_tip_leading_edge_x])
    x_x1 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 7) Fuselage axis to tip
    # The line joining the fuselage axis and the line X1
    y_fuselage_to_tip = np.array([total_wing_span / 2, wing_tip_y * 1.03])
    x_fuselage_to_tip = np.array([0.0, 0.0])
    x_fuselage_to_tip += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 7bis) Half span (Y3)
    # The line joining representing the span of the half wing
    y_y3 = np.array([0, total_wing_span / 2])
    x_y3 = np.array([0.0, 0.0])
    x_y3 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 8) Break
    # The line representing the kink (the break) of the wing
    y_break = np.array([wing_kink_y, wing_kink_y])
    x_break = np.array([wing_kink_leading_edge_x, wing_kink_leading_edge_x + wing_kink_chord * 1.7])
    x_break += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 9) MAC
    # The line representing the mean aerodynamic chord of the wing
    y_mac = np.array([mean_aerodynamic_chord_y_global, mean_aerodynamic_chord_y_global])
    x_mac = np.array([distance_root_mac_chords, distance_root_mac_chords + mean_aerodynamic_chord])
    x_mac += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 10) Perpendiculaire Down Break
    # The upper line perpendicular to the break line
    y_perp_down = np.array([wing_kink_y, wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25])
    x_perp_down = np.array([wing_kink_leading_edge_x, wing_kink_leading_edge_x])
    x_perp_down += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 11) Perpendiculaire Up Break
    # The lower line perpendicular to the break line
    y_perp_up = np.array([wing_kink_y, wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25])
    x_perp_up = np.array(
        [wing_kink_leading_edge_x + wing_kink_chord, wing_kink_leading_edge_x + wing_kink_chord]
    )
    x_perp_up += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 12) Kink chord (L2)
    # The line representing the kink chord of the wing
    y_l2 = np.array(
        [
            wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25,
            wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25,
        ]
    )
    x_l2 = np.array([wing_kink_leading_edge_x, wing_kink_leading_edge_x + wing_kink_chord])
    x_l2 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 13) Kink to leading edge (X2)
    # The line parallel to L2 and joining the line Y3 and L2
    y_x2 = np.array(
        [
            wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25,
            wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25,
        ]
    )
    x_x2 = np.array([wing_kink_leading_edge_x, 0])
    x_x2 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 14) Fuselage axis to break (Y2)
    # The line parallel to the x axis and joining the fuselage axis and the break line
    y_y2 = np.array([0, wing_kink_y])
    x_y2 = np.array(
        [
            wing_kink_leading_edge_x + wing_kink_chord * 1.4,
            wing_kink_leading_edge_x + wing_kink_chord * 1.4,
        ]
    )
    x_y2 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 15) Fuselage axis to MAC (Y0)
    # The line parallel to the x axis and joining the fuselage axis and the MAC line
    y_y0 = np.array([0, mean_aerodynamic_chord_y_global])
    x_y0 = np.array(
        [
            distance_root_mac_chords + mean_aerodynamic_chord,
            distance_root_mac_chords + mean_aerodynamic_chord,
        ]
    )
    x_y0 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 16) Perpendicular Down MAC
    # The lower line perpendicular to the MAC line
    y_down_mac = np.array(
        [
            mean_aerodynamic_chord_y_global,
            mean_aerodynamic_chord_y_global - mean_aerodynamic_chord / 2,
        ]
    )
    x_down_mac = np.array([distance_root_mac_chords, distance_root_mac_chords])
    x_down_mac += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 17) X0
    # The line parallel to the fuselage axis and joining the line Y3 with the "Perpendicular Down MAC" line
    y_x0 = np.array(
        [
            mean_aerodynamic_chord_y_global - mean_aerodynamic_chord / 2,
            mean_aerodynamic_chord_y_global - mean_aerodynamic_chord / 2,
        ]
    )
    x_x0 = np.array([distance_root_mac_chords, 0])
    x_x0 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 18) L0
    # The line parallel to the fuselage axis and representing the root chord
    y_l0 = np.array([wing_root_y / 2, wing_root_y / 2])
    x_l0 = np.array([0, wing_root_chord])
    x_l0 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 19) Continuity trailing edge
    # The line representing the continuity of the trailing edge until the fuselage axis
    y_continuity1 = np.array([wing_kink_y, 0])
    x_continuity1 = np.array(
        [
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_kink_leading_edge_x
            + wing_kink_chord
            - wing_kink_y * np.tan(np.pi * trailing_edge_kink_sweep_100_outer / 180),
        ]
    )
    x_continuity1 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 20) Continuity leading edge
    # The line representing the continuity of the leading edge until the fuselage axis
    y_continuity2 = np.array([wing_root_y, 0])
    x_continuity2 = np.array(
        [
            0,
            0 - wing_root_y * np.tan(np.pi * sweep_0 / 180),
        ]
    )
    x_continuity2 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 21) L1
    # The line joining the two previous continuity lines at the root level
    y_l1 = np.array([wing_root_y * 1.025, wing_root_y * 1.025])
    x_l1 = np.array(
        [
            wing_kink_leading_edge_x
            + wing_kink_chord
            - (wing_kink_y - wing_root_y)
            * np.sin(np.pi * trailing_edge_kink_sweep_100_outer / 180),
            0,
        ]
    )
    x_l1 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # 22) Y1
    # The line parallel to the Y3 line joining the fuselage axis line and the L1 line
    y_y1 = np.array([0, wing_root_y])
    x_y1 = np.array([-wing_root_chord * 0.2, -wing_root_chord * 0.2])
    x_y1 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords

    # X) Figure
    # Here  the different points are added on the same figure. The wing is in blue and the measuring lines are in black

    if fig is None:
        fig = go.Figure()

    scatter = go.Scatter(
        x=y, y=x, line=dict(color="blue", width=3), mode="lines", name=name, showlegend=False
    )  # wing

    scatter_fuselage = go.Scatter(
        x=y_fuselage,
        y=x_fuselage,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # fuselage axis

    scatter_l3 = go.Scatter(
        x=y_l3,
        y=x_l3,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # L3

    scatter_x1 = go.Scatter(
        x=y_x1,
        y=x_x1,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # X1

    scatter_fuselage_to_tip = go.Scatter(
        x=y_fuselage_to_tip,
        y=x_fuselage_to_tip,
        line=dict(color="gray", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Fuselage axis to tip

    scatter_y3 = go.Scatter(
        x=y_y3,
        y=x_y3,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Y3

    scatter_break = go.Scatter(
        x=y_break,
        y=x_break,
        line=dict(color="gray", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # break

    scatter_mac = go.Scatter(
        x=y_mac,
        y=x_mac,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # MAC

    scatter_perp_up = go.Scatter(
        x=y_perp_up,
        y=x_perp_up,
        line=dict(color="grey"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Perpendicular up Break

    scatter_perp_down = go.Scatter(
        x=y_perp_down,
        y=x_perp_down,
        line=dict(color="grey"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Perpendicular down Break

    scatter_l2 = go.Scatter(
        x=y_l2,
        y=x_l2,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # L2

    scatter_x2 = go.Scatter(
        x=y_x2,
        y=x_x2,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # X2

    scatter_y2 = go.Scatter(
        x=y_y2,
        y=x_y2,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Y2

    scatter_y0 = go.Scatter(
        x=y_y0,
        y=x_y0,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Y0

    scatter_down_mac = go.Scatter(
        x=y_down_mac,
        y=x_down_mac,
        line=dict(color="gray"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Perpendicular down MAC

    scatter_x0 = go.Scatter(
        x=y_x0,
        y=x_x0,
        line=dict(color="black", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # X0

    scatter_l0 = go.Scatter(
        x=y_l0,
        y=x_l0,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # L0

    scatter_continuity1 = go.Scatter(
        x=y_continuity1,
        y=x_continuity1,
        line=dict(color="gray", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Continuity1

    scatter_continuity2 = go.Scatter(
        x=y_continuity2,
        y=x_continuity2,
        line=dict(color="gray", dash="dot"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Continuity2

    scatter_l1 = go.Scatter(
        x=y_l1,
        y=x_l1,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # L1

    scatter_y1 = go.Scatter(
        x=y_y1,
        y=x_y1,
        line=dict(color="black"),
        mode="lines",
        name=name,
        showlegend=False,
    )  # Y1

    # Adding the lines to the figure
    fig.add_trace(scatter)
    fig.add_trace(scatter_fuselage)
    fig.add_trace(scatter_l3)
    fig.add_trace(scatter_x1)
    fig.add_trace(scatter_fuselage_to_tip)
    fig.add_trace(scatter_break)
    fig.add_trace(scatter_mac)
    fig.add_trace(scatter_perp_up)
    fig.add_trace(scatter_perp_down)
    fig.add_trace(scatter_l2)
    fig.add_trace(scatter_x2)
    fig.add_trace(scatter_y2)
    fig.add_trace(scatter_y0)
    fig.add_trace(scatter_x0)
    fig.add_trace(scatter_l0)
    fig.add_trace(scatter_down_mac)
    fig.add_trace(scatter_continuity1)
    fig.add_trace(scatter_continuity2)
    fig.add_trace(scatter_l1)
    fig.add_trace(scatter_y1)
    fig.add_trace(scatter_y3)

    # Creating the table with all the lengths of the variables
    d = {
        "Variable": [
            "X0 (m)",
            "X1 (m)",
            "X2 (m)",
            "Y0 (m)",
            "Y1 (m)",
            "Y2 (m)",
            "Y3 (m)",
            "L0 (m)",
            "L1 (m)",
            "L2 (m)",
            "L3 (m)",
            "MAC (m)",
            "Span (m)",
            "Wing surface (m²)",
        ],
        "Value": [
            np.round(x_x0[0] - x_x0[1], 4),  # X0
            np.round(x_x1[1] - x_x1[0], 4),  # X1
            np.round(x_x2[0] - x_x2[1], 4),  # X2
            np.round(y_y0[1] - y_y0[0], 4),  # Y0
            np.round(y_y1[1] - y_y1[0], 4),  # Y1
            np.round(y_y2[1] - y_y2[0], 4),  # Y2
            np.round(y_y3[1] - y_y3[0], 4),  # Y3
            np.round(x_l0[1] - x_l0[0], 4),  # L0
            np.round(x_l1[0] - x_l1[1], 4),  # L1
            np.round(x_l2[1] - x_l2[0], 4),  # L2
            np.round(x_l3[1] - x_l3[0], 4),  # L3
            np.round(mean_aerodynamic_chord, 4),  # MAC
            np.round(total_wing_span, 4),  # Span
            np.round(wing_area, 4),  # Wing surface
        ],
    }
    df = pd.DataFrame(data=d)
    out = widgets.Output()
    with out:
        display(df)

    # Adding all the notes to the lines
    fig.add_annotation(
        x=wing_tip_y * 1.03,
        y=(wing_tip_leading_edge_x / 2)
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="X1",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=wing_tip_y * 1.03,
        y=wing_tip_leading_edge_x
        + wing_tip_chord
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="L3",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=0,
        y=wing_root_chord * 1.6
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="Fuselage axis",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=3 * total_wing_span / 8,
        y=mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords,
        text="Y3",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=wing_kink_y,
        y=wing_kink_leading_edge_x
        + wing_kink_chord * 1.7
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="Break",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=mean_aerodynamic_chord_y_global * 1.08,
        y=distance_root_mac_chords
        + mean_aerodynamic_chord / 2
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="MAC",
        showarrow=False,
        yshift=0,
    )
    fig.add_annotation(
        x=wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25,
        y=wing_kink_leading_edge_x
        + wing_kink_chord / 2
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="L2",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=(wing_kink_y + (wing_tip_y - wing_kink_y) * 0.25),
        y=distance_root_mac_chords / 4
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="X2",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=3 * wing_kink_y / 4,
        y=wing_kink_leading_edge_x
        + wing_kink_chord * 1.4
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="Y2",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=wing_kink_y / 4,
        y=distance_root_mac_chords
        + mean_aerodynamic_chord
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="Y0",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=mean_aerodynamic_chord_y_global - mean_aerodynamic_chord / 2,
        y=3 * distance_root_mac_chords / 4
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="X0",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=(wing_root_y / 2),
        y=wing_root_chord / 3
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="L0",
        showarrow=True,
        arrowhead=1,
    )
    fig.add_annotation(
        x=wing_root_y * 1.25,
        y=wing_root_chord / 2
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="L1",
        showarrow=False,
        yshift=0,
    )
    fig.add_annotation(
        x=wing_root_y * 0.05,
        y=-wing_root_chord * 0.2
        + mac25_x_position
        - 0.25 * mean_aerodynamic_chord
        - distance_root_mac_chords,
        text="Y1",
        showarrow=True,
        arrowhead=1,
    )

    fig = go.FigureWidget(fig)
    fig.update_yaxes(constrain="domain")
    fig.update_xaxes(constrain="domain")
    fig.update_layout(
        title_text="Wing Geometry",
        title_x=0.8,
        title_y=0.98,
        xaxis_title="y",
        yaxis_title="x",
    )

    return widgets.HBox([fig, out])

def flaps_and_slats_plot(
    aircraft_file_path: str, name=None, fig=None, file_formatter=None
) -> go.FigureWidget:
    """
    Returns a figure plot of the top view of the wing with the flaps and slats added.
    Different designs can be superposed by providing an existing fig.
    Each design can be provided a name.

    :param aircraft_file_path: path of data file
    :param name: name to give to the trace added to the figure
    :param fig: existing figure to which add the plot
    :param file_formatter: the formatter that defines the format of data file. If not provided,
                           default format will be assumed.
    :return: plot figure of wing the wing with flaps and slats
    """
    variables = VariableIO(aircraft_file_path, file_formatter).read()

    wing_kink_leading_edge_x = variables["data:geometry:wing:kink:leading_edge:x:local"].value[0]
    wing_tip_leading_edge_x = variables["data:geometry:wing:tip:leading_edge:x:local"].value[0]
    wing_root_y = variables["data:geometry:wing:root:y"].value[0]
    wing_kink_y = variables["data:geometry:wing:kink:y"].value[0]
    wing_tip_y = variables["data:geometry:wing:tip:y"].value[0]
    wing_root_chord = variables["data:geometry:wing:root:chord"].value[0]
    wing_kink_chord = variables["data:geometry:wing:kink:chord"].value[0]
    wing_tip_chord = variables["data:geometry:wing:tip:chord"].value[0]
    trailing_edge_kink_sweep_100_outer = variables["data:geometry:wing:sweep_100_outer"].value[0]

    slat_chord_ratio = variables["data:geometry:slat:chord_ratio"].value[0]
    slat_span_ratio = variables["data:geometry:slat:span_ratio"].value[0]

    total_wing_span = variables["data:geometry:wing:span"].value[0]
    flaps_span_ratio = variables["data:geometry:flap:span_ratio"].value[0]
    flaps_chord_ratio = variables["data:geometry:flap:chord_ratio"].value[0]

    mean_aerodynamic_chord = variables["data:geometry:wing:MAC:length"].value[0]
    mac25_x_position = variables["data:geometry:wing:MAC:at25percent:x"].value[0]
    distance_root_mac_chords = variables["data:geometry:wing:MAC:leading_edge:x:local"].value[0]

    # 1) overall wing
    # Part of the code dedicated to the geometry of the general wing

    y = np.array(
        [0, wing_root_y, wing_kink_y, wing_tip_y, wing_tip_y, wing_kink_y, wing_root_y, 0, 0]
    )
    y = np.concatenate((-y, y))

    x = np.array(
        [
            0,
            0,
            wing_kink_leading_edge_x,
            wing_tip_leading_edge_x,
            wing_tip_leading_edge_x + wing_tip_chord,
            wing_kink_leading_edge_x + wing_kink_chord,
            wing_root_chord,
            wing_root_chord,
            0,
        ]
    )

    x = x + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x = np.concatenate((x, x))

    # 2) flaps
    # Part of the code dedicated to the flaps

    flap_chord_kink = wing_kink_chord * flaps_chord_ratio
    flap_chord_tip = wing_tip_chord * flaps_chord_ratio

    # 2.1) Inboard flap
    # Part of the code dedicated to the inboard flap

    y2 = np.array([wing_kink_y, wing_kink_y, wing_root_y, wing_root_y, wing_kink_y])
    y2 = np.concatenate((-y2, y2))

    x2 = np.array(
        [
            wing_root_chord,
            wing_root_chord - flap_chord_kink,
            wing_root_chord - flap_chord_kink,
            wing_root_chord,
            wing_root_chord,
        ]
    )

    x2 = x2 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x2 = np.concatenate((x2, x2))

    # 2.2) Outboard flap
    # Part of the code dedicated to the outboard flap

    # The points "_a" and "_b" are the ones placed on the trailing edge.
    # The points "_c" and "_d" are the projection of "_a" and "_b" normal to the trailing edge, on the wing.
    # This projection is made with a rotation matrix.
    # The points are place respecting the flaps span ratio compared to the total span of the aircraft.

    rotation_matrix = np.array(
        [
            [
                np.cos(trailing_edge_kink_sweep_100_outer * np.pi / 180),
                np.sin(trailing_edge_kink_sweep_100_outer * np.pi / 180),
            ],
            [
                -np.sin(trailing_edge_kink_sweep_100_outer * np.pi / 180),
                np.cos(trailing_edge_kink_sweep_100_outer * np.pi / 180),
            ],
        ]
    )

    y_a = wing_kink_y
    x_a = wing_root_chord

    y_b = wing_root_y + (total_wing_span / 2) * flaps_span_ratio
    x_b = (
        wing_tip_leading_edge_x
        + wing_tip_chord
        - (wing_tip_y - (wing_root_y + (total_wing_span / 2) * flaps_span_ratio))
        * np.tan(trailing_edge_kink_sweep_100_outer * np.pi / 180)
    )

    c_local = np.array([-flap_chord_tip, 0])
    x_c, y_c = rotation_matrix @ c_local + np.array([x_b, y_b])

    d_local = np.array([-flap_chord_kink, 0])
    x_d, y_d = rotation_matrix @ d_local + np.array([x_a, y_a])

    y3 = np.array([y_a, y_b, y_c, y_d, y_a])
    y3 = np.concatenate((-y3, y3))

    x3 = np.array([x_a, x_b, x_c, x_d, x_a])

    x3 = x3 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x3 = np.concatenate((x3, x3))

    # 2.3) Design line
    # Part of the code dedicated to a lign only used for an aesthetic reason.
    # This line joins the two inboard flaps

    y4 = np.array([wing_root_y])
    y4 = np.concatenate((-y4, y4))

    x4 = np.array([wing_root_chord])

    x4 = x4 + mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    # pylint: disable=invalid-name # that's a common naming
    x4 = np.concatenate((x4, x4))

    # 3) slats
    # Part of the code dedicated to the slats
    # The dimensions are given by two parameters : span_ratio and chord_ratio
    # Here the span_ratio is given by the span of the airplane minus the fuselage radius
    # the chord_ratio is given by the kink chord

    wing_span_no_fuselage = wing_tip_y - wing_root_y

    slat_y = (
        (1 - slat_span_ratio) / 2.0 * wing_span_no_fuselage
    )  # position in y of the beginning of the slats near the root
    slat_x_root = wing_tip_leading_edge_x * (1 - slat_span_ratio) / 2.0

    y5 = np.array(
        [
            slat_y + wing_root_y,
            slat_y + wing_root_y,
            wing_tip_y - slat_y,
            wing_tip_y - slat_y,
            slat_y + wing_root_y,
        ]
    )

    y6 = -y5  # slats on the other wing

    x5 = np.array(
        [
            slat_x_root,
            slat_x_root + slat_chord_ratio * wing_kink_chord,
            wing_tip_leading_edge_x * (1 - (1 - slat_span_ratio) / 2.0)
            + slat_chord_ratio * wing_kink_chord,
            wing_tip_leading_edge_x * (1 - (1 - slat_span_ratio) / 2.0),
            slat_x_root,
        ]
    )
    x5 += mac25_x_position - 0.25 * mean_aerodynamic_chord - distance_root_mac_chords
    x6 = x5

    # 4) Figure
    # Here  the different points are added on the same figure. The wing is in blue and the high lift devices in red

    if fig is None:
        fig = go.Figure()

    scatter = go.Scatter(
        x=y, y=x, line=dict(color="blue"), mode="lines", name=name, showlegend=False
    )  # wing
    scatter2 = go.Scatter(
        x=y2, y=x2, mode="lines", line=dict(color="blue", width=1), name=name, showlegend=False
    )  # first flap
    scatter3 = go.Scatter(
        x=y3, y=x3, mode="lines", line=dict(color="blue", width=1), name=name, showlegend=False
    )  # second flap
    scatter4 = go.Scatter(
        x=y4, y=x4, mode="lines", line=dict(color="blue"), name=name, showlegend=False
    )  # design line
    scatter5 = go.Scatter(
        x=y5, y=x5, line=dict(color="blue", width=1), mode="lines", name=name, showlegend=False
    )  # slats
    scatter6 = go.Scatter(
        x=y6, y=x6, line=dict(color="blue", width=1), mode="lines", name=name, showlegend=False
    )  # slats

    fig.layout = go.Layout(yaxis=dict(scaleanchor="x", scaleratio=1))

    fig.add_trace(scatter)
    fig.add_trace(scatter3)
    fig.add_trace(scatter2)
    fig.add_trace(scatter4)
    fig.add_trace(scatter5)
    fig.add_trace(scatter6)

    fig = go.FigureWidget(fig)
    fig.update_xaxes(constrain="domain")
    fig.update_yaxes(constrain="domain")
    fig.update_layout(title_text="Wing Drawing", title_x=0.5, xaxis_title="y", yaxis_title="x")

    return fig