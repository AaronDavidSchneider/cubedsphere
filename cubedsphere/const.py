"""
Variable names used through out this package
"""

FACEDIM = "face"  # index of the facedimension
j = "j"  # Y index
i = "i"  # X index
i_g = "i_g"  # X index at interface
j_g = "j_g"  # Y index at interface
k = "k"  # Z index
k_l = "k_l"  # upper Z interface
k_p1 = "k_p1"  # outer Z interface
k_u = "k_u"  # lower Z interface
Z = "Z"  # Z index
Z_l = "Z_l"  # lower Z interface
Z_p1 = "Z_p1"  # outer Z interface
Z_u = "Z_u"  # upper Z interface
Z_geo = "Z_geo"  # geometrical height
T = "T"  # Temperature
Ttave = "Ttave"  # Temperature averaged
wVeltave = "wVeltave"  # vertical velocity timeaveraged
drW = "drW"
drS = "drS"
HFacW = "hFacW"
HFacS = "hFacS"
HFacC = "hFacC"
drF = "drF"
drC = "drC"
dxC = "dxC"
dxG = "dxG"
dyC = "dyC"
dyG = "dyG"
rA = "rA"
rAz = "rAz"
rAs = "rAs"
rAw = "rAw"
lon = "lon"
lon_b = "lon_b"
lat_b = "lat_b"
lat = "lat"
AngleCS = "CS"
AngleSN = "SN"
time = "time"
dxF = "dxF"
dyU = "dyU"
dxV = "dxV"
dyF = "dyF"
W = "W"

vertical_dict = {k: Z, k_p1: Z_p1, k_l: Z_l, k_u: Z_u}

extra_exorad_variables = dict(EXOBFlux=dict(dims=['k_p1', 'j', 'i'],
                                            attrs=dict(standard_name='EXOBFlux', long_name='Bolometric Flux',
                                                       units='W/m2')),
                              EXOBFPla=dict(dims=['k_p1', 'j', 'i'],
                                            attrs=dict(standard_name='EXOBFPla', long_name='Bolometric Planetary Flux',
                                                       units='W/m2')),
                              EXOBFStar=dict(dims=['k_p1', 'j', 'i'],
                                             attrs=dict(standard_name='EXOBFStar', long_name='Bolometric Stellar Flux',
                                                        units='W/m2')),
                              EXOTend=dict(dims=['k', 'j', 'i'],
                                            attrs=dict(standard_name='EXOTend', long_name='Theta Tendency from pRT', units='K/s')),
                              EXOHR=dict(dims=['k', 'j', 'i'],
                                            attrs=dict(standard_name='EXOHR', long_name='Thermodynamic heatingrate from pRT', units='W/m3')),
                              EXOSIT=dict(dims=['j', 'i'],
                                            attrs=dict(standard_name='EXOSIT', long_name='Scattering iterations', units='')),
                              EXOFricU=dict(dims=['k', 'j', 'i_g'],
                                         attrs=dict(standard_name='EXOFricU',
                                                    long_name='friction in U direction', units='m/s2', mate='EXOFricV')),
                              EXOFricV=dict(dims=['k', 'j_g', 'i'],
                                         attrs=dict(standard_name='EXOFricV',
                                                    long_name='friction in V direction', units='m/s2', mate='EXOFricU')),
                              EXOFricHeat=dict(dims=['k', 'j', 'i'],
                                         attrs=dict(standard_name='EXOFricHeat',
                                                    long_name='Theta Tendency from rayleighfriction', units='K/s')),

                              )
