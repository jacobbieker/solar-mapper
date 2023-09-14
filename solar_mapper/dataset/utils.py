import requests, json, os, logging, math, geojson
import fsspec


def get_global_pv_mapping_polygons():
    """
    Returns a list of polygons that represent the global PV mapping
    """
    cv_polygons = geojson.load(fsspec.open("https://zenodo.org/record/5005868/files/cv_polygons.geojson").open())
    trn_polygons = geojson.load(fsspec.open("https://zenodo.org/record/5005868/files/trn_polygons.geojson").open())
    test_polygons = geojson.load(fsspec.open("https://zenodo.org/record/5005868/files/test_polygons.geojson").open())
    predicted_polygons = None #geojson.load(fsspec.open("https://zenodo.org/record/5005868/files/predicted_set.geojson").open())
    # Predicted set throws an error when opening with geoJSON, about NaN not being valid JSON.
    return {"cv": cv_polygons, "train": trn_polygons, "test": test_polygons, "predicted": predicted_polygons}

def V_inv(point1, point2, miles=False):

    # WGS 84
    a = 6378137  # meters
    f = 1 / 298.257223563
    b = 6356752.314245  # meters; b = (1 - f)a

    MILES_PER_KILOMETER = 0.621371

    MAX_ITERATIONS = 200
    CONVERGENCE_THRESHOLD = 1e-12  # .000,000,000,001
    """
    Vincenty's formula (inverse method) to calculate the distance (in
    kilometers or miles) between two points on the surface of a spheroid

    Doctests:
    >>> vincenty((0.0, 0.0), (0.0, 0.0))  # coincident points
    0.0
    >>> vincenty((0.0, 0.0), (0.0, 1.0))
    111.319491
    >>> vincenty((0.0, 0.0), (1.0, 0.0))
    110.574389
    >>> vincenty((0.0, 0.0), (0.5, 179.5))  # slow convergence
    19936.288579
    >>> vincenty((0.0, 0.0), (0.5, 179.7))  # failure to converge
    >>> boston = (42.3541165, -71.0693514)
    >>> newyork = (40.7791472, -73.9680804)
    >>> vincenty(boston, newyork)
    298.396057
    >>> vincenty(boston, newyork, miles=True)
    185.414657
    """

    # short-circuit coincident points
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return 0.0,0,0

    U1 = math.atan((1 - f) * math.tan(math.radians(point1[0])))
    U2 = math.atan((1 - f) * math.tan(math.radians(point2[0])))
    L = math.radians(point2[1] - point1[1])
    Lambda = L

    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)

    for iteration in range(MAX_ITERATIONS):
        sinLambda = math.sin(Lambda)
        cosLambda = math.cos(Lambda)
        sinSigma = math.sqrt((cosU2 * sinLambda) ** 2 +
                             (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        try:
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
        except ZeroDivisionError:
            cos2SigmaM = 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        LambdaPrev = Lambda
        Lambda = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma *
                                               (cos2SigmaM + C * cosSigma *
                                                (-1 + 2 * cos2SigmaM ** 2)))
        if abs(Lambda - LambdaPrev) < CONVERGENCE_THRESHOLD:
            break  # successful convergence
    else:
        return None  # failure to converge

    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma *
                                                       (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM *
                                                       (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    s = b * A * (sigma - deltaSigma)


    num = (math.cos(U2)*math.sin(Lambda))
    den = (math.cos(U1)*math.sin(U2)-math.sin(U1)*math.cos(U2)*math.cos(Lambda))

    #print 'num',num
    #print 'den',den
    alpha1 = math.atan2(num,den)

    if alpha1<0:
        alpha1+=2*math.pi



    num = (math.cos(U1)*math.sin(Lambda))
    den = (-1.0*math.sin(U1)*math.cos(U2)+math.cos(U1)*math.sin(U2)*math.cos(Lambda))
    #print 'num',num
    #print 'den',den
    alpha2 = math.atan2(num,den)

    if alpha2<0:
        alpha2+=2*math.pi


    s /= 1000  # meters to kilometers
    if miles:
        s *= MILES_PER_KILOMETER  # kilometers to miles

    return round(s, 6), math.degrees(alpha1), math.degrees(alpha2)

def V_dir(point1, s, alpha1,miles=False):
    #print 'v_dir'
    # WGS 84
    a = 6378137  # meters
    f = 1 / 298.257223563
    b = 6356752.314245  # meters; b = (1 - f)a

    MILES_PER_KILOMETER = 0.621371

    MAX_ITERATIONS = 200
    CONVERGENCE_THRESHOLD = 1e-12  # .000,000,000,001
    """
    Vincenty's formula (inverse method) to calculate the distance (in
    kilometers or miles) between two points on the surface of a spheroid

    Doctests:
    >>> vincenty((0.0, 0.0), (0.0, 0.0))  # coincident points
    0.0
    >>> vincenty((0.0, 0.0), (0.0, 1.0))
    111.319491
    >>> vincenty((0.0, 0.0), (1.0, 0.0))
    110.574389
    >>> vincenty((0.0, 0.0), (0.5, 179.5))  # slow convergence
    19936.288579
    >>> vincenty((0.0, 0.0), (0.5, 179.7))  # failure to converge
    >>> boston = (42.3541165, -71.0693514)
    >>> newyork = (40.7791472, -73.9680804)
    >>> vincenty(boston, newyork)
    298.396057
    >>> vincenty(boston, newyork, miles=True)
    185.414657
    """

    #alpha1 in degrees
    alpha1=math.radians(alpha1)
    U1 = math.atan((1.0-f)*math.tan(math.radians(point1[0])))
    #print U1
    sigma1 = math.atan2((math.tan(U1)),(math.cos(alpha1)))
    sinAlpha=math.cos(U1)*math.sin(alpha1)
    cosSqAlpha=1.0-(sinAlpha**2)
    uSq = cosSqAlpha*(a**2-b**2)/(b**2)
    A = 1 + uSq/16384.0*(4096.0+uSq*(-768.0+uSq*(320.0-175*uSq)))
    B = uSq/1024*(256+uSq*(-128+uSq*(74-47*uSq)))

    sigma=s/b/A
    #print sigma
    for iteration in range(MAX_ITERATIONS):

        sigma2m = 2*sigma1+sigma
        deltasigma = B*math.sin(sigma)*(math.cos(sigma2m)+1.0/4*B*(math.cos(sigma)*(-1+2*(math.cos(sigma2m)**2))-1.0/6*B*math.cos(sigma2m)*(-3+4*(math.sin(sigma)**2))*(-3+4*(math.cos(sigma2m)**2))))
        sigmaprev = sigma
        sigma = s/b/A+deltasigma
        #print sigma
        if abs(sigma - sigmaprev) < CONVERGENCE_THRESHOLD:
            #print 'converge'
            break  # successful convergence
    else:
        print ('no converg')
        return None  # failure to converge


    num = math.sin(U1)*math.cos(sigma)+math.cos(U1)*math.sin(sigma)*math.cos(alpha1)
    den = (1.0-f)*math.sqrt(sinAlpha**2+(math.sin(U1)*math.sin(sigma)-math.cos(U1)*math.cos(sigma)*math.cos(alpha1))**2)
    #print num
    #print den
    lat2= math.atan2(num,den)

    num=math.sin(sigma)*math.sin(alpha1)
    den = math.cos(U1)*math.cos(sigma)-math.sin(U1)*math.sin(sigma)*math.cos(alpha1)
    Lambda = math.atan2(num,den)

    C = f/16.0*(cosSqAlpha*(4+f*(4.0-3.0*cosSqAlpha)))
    L = Lambda - (1.0-C)*f*sinAlpha*(sigma+C*math.sin(sigma)*(math.cos(sigma2m)+C*math.cos(sigma)*(-1+2.0*(math.cos(sigma2m)**2))))

    L2 = math.radians(point1[1])+L
    num = sinAlpha
    den = -1*math.sin(U1)*math.sin(sigma)+math.cos(U1)*math.cos(sigma)*math.cos(alpha1)
    #print num
    #print den
    alpha2 = math.atan2(num,den)
    if alpha2<0:
        alpha2+=math.pi*2
    #print alpha2
    # short-circuit coincident points
    return (math.degrees(lat2),math.degrees(L2)),math.degrees(alpha2)

def get_utm_zone(lat,lon):
    """A function to grab the UTM zone number for any lat/lon location
    """
    zone_str = str(int((lon + 180)/6) + 1)

    if ((lat>=56.) & (lat<64.) & (lon >=3.) & (lon <12.)):
        zone_str = '32'
    elif ((lat >= 72.) & (lat <84.)):
        if ((lon >=0.) & (lon<9.)):
            zone_str = '31'
        elif ((lon >=9.) & (lon<21.)):
            zone_str = '33'
        elif ((lon >=21.) & (lon<33.)):
            zone_str = '35'
        elif ((lon >=33.) & (lon<42.)):
            zone_str = '37'

    return zone_str