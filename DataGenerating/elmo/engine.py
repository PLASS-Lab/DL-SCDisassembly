import numpy as np
import os
from enum import IntEnum, unique

from .utils import binary_writing
from .config import ELMO_TOOL_REPOSITORY

@unique
class Instruction(IntEnum):
    EOR = 0
    LSL = 1
    STR = 2
    LDR = 3
    MUL = 4
    OTHER = 5
    
# Short name for 'Instruction' class
Instr = Instruction

PREVIOUS = 0
CURRENT = 1
SUBSEQUENT = 2

class ELMOEngine:
    ### Initialization
    def __init__(self):
        self.load_coefficients()
        self.reset_points()
    
    def _extract_data(self, nb):
        coeffs = self.coefficients[self.pos:self.pos+nb]
        self.pos += nb
        return coeffs

    def load_coefficients(self):
        """ Load the coefficients for the ELMO model about power leakage """
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ELMO_TOOL_REPOSITORY,
            'coeffs.txt',
        )
        self.coefficients = None
        with open(filename, 'r') as _file:
            self.coefficients = np.array([list(map(float, line.split())) for line in _file.readlines()[:2153]])
        
        if self.coefficients is None:
            raise IOError('Problem to read the coefficients.')
        
        self.pos = 0
        
        self.constant = np.squeeze(self._extract_data(1))
        
        self.PrvInstr = self._extract_data(4)
        self.SubInstr = self._extract_data(4)
        
        self.Operand1 = self._extract_data(32)
        self.Operand2 = self._extract_data(32)
        self.BitFlip1 = self._extract_data(32)
        self.BitFlip2 = self._extract_data(32)
        
        self.HWOp1PrvInstr = self._extract_data(4)
        self.HWOp2PrvInstr = self._extract_data(4)
        self.HDOp1PrvInstr = self._extract_data(4)
        self.HDOp2PrvInstr = self._extract_data(4)
        self.HWOp1SubInstr = self._extract_data(4)
        self.HWOp2SubInstr = self._extract_data(4)
        self.HDOp1SubInstr = self._extract_data(4)
        self.HDOp2SubInstr = self._extract_data(4)
        
        self.Operand1_bitinteractions = self._extract_data(496)
        self.Operand2_bitinteractions = self._extract_data(496)
        self.BitFlip1_bitinteractions = self._extract_data(496)
        self.BitFlip2_bitinteractions = self._extract_data(496)
    
    ### Computation core
    def _dot(self, a, b):
        return np.sum(a * b, axis=0)
        
    def calculate_point(self, triplet, previous_ops, current_ops, debug=False):
        nb_points = triplet.shape[1]
        instructiontype = triplet[CURRENT]
        instructiontype = instructiontype % 5 # Type 5 = Instruction was not profiled
                
        # Previous
        previous_instruction_typedec = triplet[PREVIOUS]
        previous_instruction_type = np.zeros((5, nb_points))
        for i in range(nb_points):
            if previous_instruction_typedec[i] < 5:
                previous_instruction_type[previous_instruction_typedec[i],i] = 1
        
        # Current
        (current_op1_binary, hw_op1) = binary_writing(current_ops[0], with_hamming=True)
        (current_op2_binary, hw_op2) = binary_writing(current_ops[1], with_hamming=True)

        (current_op1_bitflip, hd_op1) = binary_writing(previous_ops[0] ^ current_ops[0], with_hamming=True)
        (current_op2_bitflip, hd_op2) = binary_writing(previous_ops[1] ^ current_ops[1], with_hamming=True)
        
        current_instruction_typedec = instructiontype
        current_instruction_type = np.zeros((5, nb_points))
        for i in range(nb_points):
            if triplet[CURRENT,i] < 5:
                current_instruction_type[current_instruction_typedec[i],i] = 1
        
        # Subsequent
        subsequent_instruction_typedec = triplet[SUBSEQUENT]
        subsequent_instruction_type = np.zeros((5, nb_points))
        for i in range(nb_points):
            if subsequent_instruction_typedec[i] < 5:
                subsequent_instruction_type[subsequent_instruction_typedec[i],i] = 1

        # Component variables
        PrvInstr_data = self._dot( previous_instruction_type[1:], self.PrvInstr[:,instructiontype] )
        SubInstr_data = self._dot( subsequent_instruction_type[1:], self.SubInstr[:,instructiontype] )
        
        Operand1_data = self._dot( current_op1_binary, self.Operand1[:,instructiontype] )
        Operand2_data = self._dot( current_op2_binary, self.Operand2[:,instructiontype] )
        BitFlip1_data = self._dot( current_op1_bitflip, self.BitFlip1[:,instructiontype] )
        BitFlip2_data = self._dot( current_op2_bitflip, self.BitFlip2[:,instructiontype] )
        
        HWOp1PrvInstr_data = hw_op1 * self._dot(previous_instruction_type[1:], self.HWOp1PrvInstr[:,instructiontype])
        HWOp2PrvInstr_data = hw_op2 * self._dot(previous_instruction_type[1:], self.HWOp2PrvInstr[:,instructiontype])
        HDOp1PrvInstr_data = hd_op1 * self._dot(previous_instruction_type[1:], self.HDOp1PrvInstr[:,instructiontype])
        HDOp2PrvInstr_data = hd_op2 * self._dot(previous_instruction_type[1:], self.HDOp2PrvInstr[:,instructiontype])
        HWOp1SubInstr_data = hw_op1 * self._dot(subsequent_instruction_type[1:], self.HWOp1SubInstr[:,instructiontype])
        HWOp2SubInstr_data = hw_op2 * self._dot(subsequent_instruction_type[1:], self.HWOp2SubInstr[:,instructiontype])
        HDOp1SubInstr_data = hd_op1 * self._dot(subsequent_instruction_type[1:], self.HDOp1SubInstr[:,instructiontype])
        HDOp2SubInstr_data = hd_op2 * self._dot(subsequent_instruction_type[1:], self.HDOp2SubInstr[:,instructiontype])
        
        Operand1_bitinteractions_data = np.zeros((nb_points))
        Operand2_bitinteractions_data = np.zeros((nb_points))
        BitFlip1_bitinteractions_data = np.zeros((nb_points))
        BitFlip2_bitinteractions_data = np.zeros((nb_points))
        
        count = 0
        for i in range(32):
            for j in range(i+1,32):
                Operand1_bitinteractions_data += self.Operand1_bitinteractions[count,instructiontype] * current_op1_binary[i] * current_op1_binary[j]
                Operand2_bitinteractions_data += self.Operand2_bitinteractions[count,instructiontype] * current_op2_binary[i] * current_op2_binary[j]

                BitFlip1_bitinteractions_data += self.BitFlip1_bitinteractions[count,instructiontype] * current_op1_bitflip[i] * current_op1_bitflip[j]
                BitFlip2_bitinteractions_data += self.BitFlip2_bitinteractions[count,instructiontype] * current_op2_bitflip[i] * current_op2_bitflip[j]

                count += 1
                
        power = self.constant[instructiontype] \
                    + PrvInstr_data + SubInstr_data \
                    + Operand1_data + Operand2_data \
                    + BitFlip1_data + BitFlip2_data \
                    + HWOp1PrvInstr_data + HWOp2PrvInstr_data \
                    + HDOp1PrvInstr_data + HDOp2PrvInstr_data \
                    + HWOp1SubInstr_data + HWOp2SubInstr_data \
                    + HDOp1SubInstr_data + HDOp2SubInstr_data \
                    + Operand1_bitinteractions_data + Operand2_bitinteractions_data \
                    + BitFlip1_bitinteractions_data + BitFlip2_bitinteractions_data
        
        for i in range(nb_points):
            if triplet[CURRENT,i] == 5:
                power[i] = self.constant[triplet[CURRENT,i]]
                
        if debug:
            print([self.constant[instructiontype], \
                       PrvInstr_data, SubInstr_data, \
                       Operand1_data, Operand2_data, \
                       BitFlip1_data, BitFlip2_data, \
                       HWOp1PrvInstr_data, HWOp2PrvInstr_data, \
                       HDOp1PrvInstr_data, HDOp2PrvInstr_data, \
                       HWOp1SubInstr_data, HWOp2SubInstr_data, \
                       HDOp1SubInstr_data, HDOp2SubInstr_data, \
                       Operand1_bitinteractions_data, Operand2_bitinteractions_data, \
                       BitFlip1_bitinteractions_data, BitFlip2_bitinteractions_data])
        return power
    
    ### To manage studied points
    def reset_points(self):
        """ Reset all the points previously added """
        self.points = []
        self.power = None

    def add_point(self, triplet, previous_ops, current_ops):
        """ Add a new point to analyse """
        self.points.append((triplet, previous_ops, current_ops))    
        
    def run(self):
        """ Compute the power leakage of all the points previously added 
        Store the results in 'self.power'
        """
        nb_points = len(self.points)
        triplet = np.array([p[0] for p in self.points]).T # shape = (3, nb_points)
        previous_ops = np.array([p[1] for p in self.points]).T # shape = (2, nb_points)
        current_ops = np.array([p[2] for p in self.points]).T # shape = (2, nb_points)
        
        self.power = self.calculate_point(triplet, previous_ops, current_ops)
    
    def oneshot_point(self, triplet, previous_ops, current_ops):
        """ Compute the power of a single point
                defined by 'triplet', 'previous_ops', and 'current_ops'
        """
        self.reset_points()
        self.add_point(triplet, previous_ops, current_ops)
        self.run()
        return self.power
