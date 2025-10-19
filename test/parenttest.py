class A:
    def hello(self):
        return A.yes(self)
    # end

    def yes(self):
        return 'A.yes'
    # end
# end


class AA(A):
    def hello(self):
        return super().hello()
    # end

    def yes(self):
        return 'AA.yes'
    # end



print(AA().hello())