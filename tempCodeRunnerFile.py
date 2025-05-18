if p2 >= p1:
            p1_new = round((p1 + p2 - new_d) / 2)
            p2_new = p1_new + new_d
        else:
            p1_new = round((p1 + p2 + new_d) / 2)
            p2_new = p1_new - new_d