"""
Estimation of passenger seats weight
"""

#  This file is part of FAST : A framework for rapid Overall Aircraft Design
#  Copyright (C) 2020  ONERA/ISAE
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
import numpy as np
from openmdao.core.explicitcomponent import ExplicitComponent

from fastoad.modules.options import AIRCRAFT_TYPE_OPTION


class PassengerSeatsWeight(ExplicitComponent):
    # TODO: Document equations. Cite sources
    """ Passenger seats weight estimation (D2) """

    def initialize(self):
        self.options.declare(AIRCRAFT_TYPE_OPTION, types=float, default=2.0)

    def setup(self):
        self.add_input('data:TLAR:NPAX', val=np.nan)
        self.add_input('tuning:weight:furniture:passenger_seats:mass:k', val=1.)
        self.add_input('tuning:weight:furniture:passenger_seats:mass:offset', val=0., units='kg')

        self.add_output('data:weight:furniture:passenger_seats:mass', units='kg')

    def compute(self, inputs, outputs
                , discrete_inputs=None, discrete_outputs=None):
        npax = inputs['data:TLAR:NPAX']
        k_d2 = inputs['tuning:weight:furniture:passenger_seats:mass:k']
        offset_d2 = inputs['tuning:weight:furniture:passenger_seats:mass:offset']

        aircraft_type = self.options[AIRCRAFT_TYPE_OPTION]
        if aircraft_type == 1.0:
            k_ps = 9.0
        if aircraft_type in (2.0, 3.0):
            k_ps = 10.0
        if aircraft_type in (4.0, 5.0):
            k_ps = 11.0
        if aircraft_type == 6.0:
            k_ps = 0.

        temp_d2 = k_ps * npax
        outputs['data:weight:furniture:passenger_seats:mass'] = k_d2 * temp_d2 + offset_d2
