vars = dict()

def add_var(all_vars, the_var, name):
    vars[id(the_var)] = (name, all_vars, [the_var])

def remove_var(the_var):
    pass

def update():
    for i in vars:
        i[2].append(i[1][i[0]])

def output():
    pass