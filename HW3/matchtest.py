a = 0

while a < 3:
    a += 1
    match a:
        case 1:
            print('in 1')
        case 2:
            print('in 2')
            continue
        case _:
            print('in _')
            continue
        # end
    # end
# end