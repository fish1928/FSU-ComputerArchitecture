from actions import Action


class InstructionDecoder:

    BITS_ADDRESS_DEFAULT = 32

    def __init__(self, bits_tag, bits_index, bits_offset):
        self.bits_tag = bits_tag
        self.bits_index = bits_index
        self.bits_offset = bits_offset
    # end

    def decode(self, str_instruction) -> Action:
        action, _, address_hex = str_instruction.split()
        address_binary = bin(int(address_hex,16))[2:]        #'0b***'
        address_32bits = self._patch_binary_str(address_binary, self.__class__.BITS_ADDRESS_DEFAULT)

        int_tag = int(address_32bits[:self.bits_tag], 2)
        int_index = int(address_32bits[self.bits_tag:self.bits_tag + self.bits_index], 2) if self.bits_index else 0
        int_offset = int(address_32bits[self.bits_tag + self.bits_index:], 2)

        print('in InstructionDecoder.decode {}, tag: {}/{}({}), index: {}/{}({}), offset: {}/{}({})'.format(
            action, int_tag, pow(2, self.bits_tag), self.bits_tag, int_index, pow(2,self.bits_index), self.bits_index, int_offset, pow(2, self.bits_offset), self.bits_offset))
            
        return Action.get_action_klass(action)(int_tag, int_index, int_offset)
    # end

    def _patch_binary_str(self, input, bits_target):
        if len(input) > bits_target:
            return input[-bits_target:]

        input = '0'*(bits_target - len(input)) + input
        return input
    # end
# end


