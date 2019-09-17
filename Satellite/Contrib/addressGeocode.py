import requests

def addressGeocode(address, outSR = "4326"):
    geoCodeUrl = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    
    #clean up the address for url encoding
    address = address.replace(" ", "+")
    address = address.replace(",", "%3B")

    #send address to geocode service
    lookup = requests.get(geoCodeUrl + "?SingleLine=" + address + "&outSR=" + outSR + "&maxLocations=1&f=pjson")
    data = lookup.json()

    if data["candidates"]:
        #results
        coords = data["candidates"][0]["location"]
        return coords
    else:
        #no results
        return "Address not geocoded: " + address

#Geocode = addressGeocode("49 Mount Street Eaglemont Vic 3084, Australia")
#print(Geocode)
