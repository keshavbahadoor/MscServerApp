print 'testing stuff here'

def h_decorate(func):
    def func_wrapper(name):
        return '<h1>{0}</h1>'.format(func(name))
    return func_wrapper

def p_decorate(func):
    def func_wrapper(name):
        return '<p>{0}</p>'.format(func(name))
    return func_wrapper

@h_decorate
@p_decorate
def get_text(name):
    return 'Ny mane is: {0}'.format(name)

print get_text('keshav')