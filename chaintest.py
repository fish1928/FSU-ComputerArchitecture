from typing import Self, Tuple


class ChainUnit():
    def __init__(self, id_unit):
        self.next = None
        self.previous = None
        self.id_unit = id_unit

        self._current = None
    # end

    def set_next(self, unit_next):
        self.next = unit_next
    # end

    def get_next(self) -> Self:
        return self.next
    # end

    def set_previous(self, unit_previous):
        self.previous = unit_previous
    # end
    
    def get_previous(self) -> Self:
        return self.previous
    # end

    def is_tail(self):
        return True if self.previous is None else False
    # end

    def is_head(self):
        return True if self.next is None else False
    # end

    def get_id(self) -> int:
        return self.id_unit
    # end

    def __next__(self) -> Self:
        if self._iter_current is None:
            raise StopIteration
        else:
            target = self._iter_current
            self._iter_current = self._iter_current.get_next()
            return target
        # end
    # end

    def __iter__(self):
        self._iter_current = self
        return self
    # end
# end


class ChainLine():  # factory

    INDEX_HEAD = -2
    INDEX_TAIL = -1

    @classmethod
    def generate_line(cls, num_units) -> Tuple[ChainUnit, ChainUnit, list]:
        tail = ChainUnit(-1)

        previous = tail
        for i in range(num_units):
            current = ChainUnit(i)
            previous.set_next(current)
            current.set_previous(previous)
            previous = current
        # end

        head = ChainUnit(-2)
        previous.set_next(head)
        head.set_previous(previous)

        index_line = [None]*(num_units+2)

        for unit in tail:
            index_line[unit.get_id()] = unit
        # end

        return head, tail, index_line
    # end
# end


head, tail, index_line = ChainLine.generate_line(10)
print([u.get_id() for u in list(tail)])