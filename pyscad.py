class Transform:

    def __init__(self, name, *params):
        self.name = name
        self.params = params

    def compile(self, path):
        ident = ' ' * 4 * len(path)
        prms = ', '.join(map(str,self.params))
        return ident + '{self.name}([{prms}])'.format(self=self, prms=prms)

    def __str__(self):
        return self.compile().strip()



class Solid:
    transforms = ()
    solids = ()
    params = {}

    def copy(self, transforms=None, solids=None):
        new = self.__class__()
        new.transforms = self.transforms
        new.solids = self.solids
        new.params = self.params

        if transforms:
            new.transforms += transforms
        if solids:
            new.solids += solids

        return new

    def move(self, x=0, y=0, z=0):
        return self.copy(
            transforms=(Transform('translate', x, y, z),))

    def rotate(self, x=0, y=0, z=0):
        return self.copy(
            transforms=(Transform('rotate', x, y, z),))

    def scale(self, x, y=None, z=None):
        if y is None and z is None:
            y = z = x
        return self.copy(
            transforms=(Transform('scale', x, y, z),))

    def __add__(self, other):
        if isinstance(other, Solid):
            return Union(self, other)

    def __sub__(self, other):
        if isinstance(other, Solid):
            return Diff(self, other)

    def compile(self, path=[]):
        ident = ' ' * 4 * len(path)
        out = []
        for t in self.transforms:
            out.append(t.compile(path))

        if self.params:
            prms = ', '.join('{}={}'.format(k,v) for (k,v) in sorted(self.params.items()))
            out.append(ident + '{self.name}({prms})'.format(self=self, prms=prms))
        else:
            out.append(ident + '{self.name}()'.format(self=self))

        if self.solids:
            out.append(ident + '{')
            for solid in self.solids:
                out.append(solid.compile(path + [self]))
            out[-1] = out[-1].rstrip('\n')
            out.append(ident + '}')
            return '\n'.join(out) + '\n'
        else:
            return '\n'.join(out) + ';\n'

    def __str__(self):
        return ' '.join(self.compile().split())


class Union(Solid):
    name = 'union'

    def __init__(self, *solids):
        self.solids = solids

    def __add__(self, other):
        if isinstance(other, Union) and not other.transforms:
            return self.copy(solids=other.solids)
        super().__add__(other)


class Diff(Solid):
    name = 'difference'

    def __init__(self, *solids):
        self.solids = solids

    def __sub__(self, other):
        if isinstance(other, Union) and not other.transforms:
            return self.copy(solids=other.solids)
        super().__sub__(other)


class Cylinder(Solid):
    name = 'cylinder'

    def __init__(self, r : float = 1.0,
                       s : float = 1.0):
        self.params = dict(r=r, s=s)


if __name__ == '__main__':
    c = Cylinder(r=10).move(y=.5, z=-.5)
    g = c + c.rotate(90,0,0) - c.move(x=-1).scale(2).rotate(0,45,0)

    print(g.compile())
