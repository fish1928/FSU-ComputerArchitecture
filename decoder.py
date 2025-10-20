import os
from actions import Action


class InstructionDecoder:

    BITS_ADDRESS_DEFAULT = 32

    def __init__(self, bits_tag, bits_index, bits_offset):
        self.bits_tag = bits_tag
        self.bits_index = bits_index
        self.bits_offset = bits_offset
    # end

    def decode(self, str_instruction) -> Action:
        action, address_patch_10, address_hex = str_instruction.split()
        address_new = int(address_patch_10, 10) + int(address_hex,16)
        address_binary = bin(address_new)[2:]        #'0b***'
        address_32bits = self._patch_binary_str(address_binary, self.__class__.BITS_ADDRESS_DEFAULT)

        int_tag = int(address_32bits[:self.bits_tag], 2)
        int_index = int(address_32bits[self.bits_tag:self.bits_tag + self.bits_index], 2) if self.bits_index else 0
        int_offset = int(address_32bits[self.bits_tag + self.bits_index:], 2)

        if os.getenv('ENABLE_INDEX'):
            return Action.get_action_klass(action)(int_tag, int_index, int_offset)
        else:
            return Action.get_action_klass(action)(int_tag, int_index, 0)
    # end

    def _patch_binary_str(self, input, bits_target):
        if len(input) > bits_target:
            return input[-bits_target:]

        input = '0'*(bits_target - len(input)) + input
        return input
    # end
# end