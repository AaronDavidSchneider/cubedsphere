"""
Variable names used through out this package
"""

FACEDIM = "face"       # index of the facedimension
j = "j"                # Y index
i = "i"                # X index
i_g = "i_g"            # X index at interface
j_g = "j_g"            # Y index at interface
k = "k"                # Z index
k_l = "k_l"            # upper Z interface
k_p1 = "k_p1"          # outer Z interface
k_u = "k_u"            # lower Z interface
Z = "Z"                # Z index
Z_l = "Z_l"            # lower Z interface
Z_p1 = "Z_p1"          # outer Z interface
Z_u = "Z_u"            # upper Z interface
T = "T"                # Temperature
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

vertical_dict = {k:Z, k_p1:Z_p1, k_l:Z_l, k_u:Z_u}