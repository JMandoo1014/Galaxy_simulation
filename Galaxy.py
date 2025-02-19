import numpy as np

class Galaxy:

    def __init__(self, galmass, ahalo, vhalo, rhalo, galpos, galvel):
        self.galmass = galmass
        self.ahalo   = ahalo
        self.vhalo   = vhalo
        self.rhalo   = rhalo
        self.galpos  = galpos
        self.galvel  = galvel
        self.galacc  = np.full((3, 1), 0.)

    def setPosvel(self, pos, vel):
        self.galpos = pos
        self.galvel = vel

    def scaleMass(self, massFact):
        self.galmass = self.galmass * massFact
        self.vhalo = 1.0 * massFact ** 0.25
        self.ahalo = 0.1 * massFact ** 0.5
        a2 = -self.galmass / (self.vhalo**2)
        a1 = -2.0 * self.ahalo * self.galmass / (self.vhalo**2)
        a0 = -self.galmass * (self.ahalo ** 2) / (self.vhalo**2)
        q  = a1/3.0 - (a2**2)/9.0
        r  = (a1*a2 - 3.0*a0)/6.0 - (a2**3)/27.0
        s1 = (r + np.sqrt(q**3 + r**2))**(1.0/3.0)
        s2 = (r - np.sqrt(q**3 + r**2))**(1.0/3.0)
        self.rhalo = (s1+s2) - a2/3.0

    def moveGalaxy(self, dtime):
        newpos = self.galpos + self.galvel * dtime + 0.5 * self.galacc * (dtime**2)
        newvel = self.galvel + self.galacc * dtime
        self.galpos = newpos
        self.galvel = newvel

    def acceleration(self, posin):
        G = 1.0
        dpos = posin - self.galpos
        r = np.sqrt(np.sum(dpos**2, axis=0))
        AccMag = -(G * self.interiorMass(r))/(r**2)
        calcacc = (dpos*AccMag)/r
        return calcacc

    def potential(self, posin):
        G = 1.0
        dpos = posin - self.galpos
        r = np.sqrt(np.sum(dpos**2, axis=0))
        pot = G * self.interiorMass(r)/r
        return pot

    def interiorMass(self, r):
        indices = r < self.rhalo
        intmass = np.full(r.shape, 0.)
        if intmass[indices].shape != (0,):
            intmass[indices] = (self.vhalo**2) * (r[indices]**3) / ((self.ahalo+r[indices])**2)
        if intmass[~indices].shape != (0,):
            intmass[~indices] = self.galmass
        return intmass

    def density(self, r):
        rinner = r * 0.99
        router = r * 1.01
        minner = self.interiorMass(rinner)
        mouter = self.interiorMass(router)
        dm = mouter - minner
        vol = (4.0/3.0) * np.pi * ((router**3) - (rinner**3))
        dens = dm / vol
        return dens

    def dynFriction(self, pmass, ppos, pvel):
        G = 1.0
        In_gamma = 3.0
        dv = pvel - self.galvel
        v = np.linalg.norm(dv)
        dr = ppos - self.galpos
        r = np.linalg.norm(dr)
        galrho = self.density(r)
        fricmag = 4.0*np.pi*G*In_gamma*pmass*galrho*v/((1+v)**3)
        friction = (-dv/v)*fricmag
        return friction
