### In this file is defined a Python class to manipulate the simualtion project.
###  - This class must be inherited from th class 'SimulationProject' (no need to import it)
###  - You can use here the function "write(input_file, uint, nb_bits=16)"
###            to write an integer of 'nb_bits' bits in the 'input_file' (no need to import it too).
### To get this simulation class in Python scripts, please use the functions in manage.py as
###  - search_simulations(repository)
###  - get_simulation(repository, classname=None)
###  - get_simulation_via_classname(classname)

class KyberNTTSimulation(SimulationProject):
    KYBER_K = 2 #k=2 for Kyber512
    KYBER_N = 256 #n=256 for Kyber512
    
    @classmethod
    def get_binary_path(cl):
        return 'project.bin'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_input(self, input):
        """ Write into the 'input' file of ELMO tool
                the parameters and the challenges for the simulation """
        super().set_input(input)

    def set_input_for_each_challenge(self, input, challenge):
        """ Write into the 'input' file of ELMO tool
                the 'challenge' for the simulation """
        secret = challenge

        # Write the secret vector
        for j in range(self.KYBER_K):
            for k in range(self.KYBER_N):
                write(input, secret[j,k])
                
    def get_test_challenges(self):
        import numpy as np
        just_ones = np.ones((self.KYBER_K, self.KYBER_N), dtype=int)
        return [
             0 * just_ones,
             1 * just_ones,
            -2 * just_ones,
        ]
        
    def get_random_challenges(self, nb_challenges=5):
        import numpy as np
        return [ np.random.choice(
            [-2, -1, 0, 1, 2],
            (self.KYBER_K, self.KYBER_N),
            p=[1/16, 4/16, 6/16, 4/16, 1/16],
        ) for _ in range(nb_challenges) ]
