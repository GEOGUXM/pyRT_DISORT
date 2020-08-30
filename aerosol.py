import numpy as np


# Make the super class
class Aerosol(object):
    def check_valid_asymmetry_parameter(self, g):
        """Check the HG asymmetry parameter is valid

        Parameters
        ----------
        g: float
            The Henyey-Greenstein asymmetry parameter. Can range from [-1, 1]

        Returns
        -------
        True if the parameter is within [-1, 1]; False otherwise
        """
        if -1 <= g <= 1:
            return True
        else:
            return False

    def make_hg_phase_function(self, g, theta):
        """Evaluate the Henyey-Greenstein phase function for a generalized aerosol

        Parameters
        ----------
        g: float
            The Henyey-Greenstein asymmetry parameter. Can range from [-1, 1]
        theta: float
            The angle at which to evaluate the HG phase function

        Returns
        -------

        """
        if self.check_valid_asymmetry_parameter(g):
            return 1 / (4*np.pi) * (1 - g**2) / (1 + g**2 - 2*g*np.cos(theta))**(3/2)
        else:
            print('The asymmetry parameter is not valid. Ensure it\'s between [-1, 1]')
            return


