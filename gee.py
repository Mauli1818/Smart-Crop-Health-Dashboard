import ee
from datetime import datetime, timedelta

# Google Earth Engine Initialize
ee.Initialize(project="khaupiu-location")


def get_latest_image(polygon_coords):

    farm = ee.Geometry.Polygon([polygon_coords])

    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    start_date = (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d")

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(farm)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .sort("system:time_start", False)
    )

    if collection.size().getInfo() == 0:
        return None

    return collection.first()


def analyze_crop(polygon_coords):

    try:

        image = get_latest_image(polygon_coords)

        if image is None:
            return {
                "status": False,
                "message": "No Sentinel-2 image found."
            }

        farm = ee.Geometry.Polygon([polygon_coords])

        # NDVI
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

        ndvi_value = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=farm,
            scale=10,
            maxPixels=1e9
        ).get("NDVI").getInfo()

        # NDWI
        ndwi = image.normalizedDifference(["B8", "B11"]).rename("NDWI")

        ndwi_value = ndwi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=farm,
            scale=10,
            maxPixels=1e9
        ).get("NDWI").getInfo()

        # EVI
        evi = image.expression(
            '2.5*((NIR-RED)/(NIR+6*RED-7.5*BLUE+1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        )

        evi_value = evi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=farm,
            scale=10,
            maxPixels=1e9
        ).values().get(0).getInfo()

        # SAVI
        savi = image.expression(
            '((NIR-RED)/(NIR+RED+0.5))*1.5',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4')
            }
        )

        savi_value = savi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=farm,
            scale=10,
            maxPixels=1e9
        ).values().get(0).getInfo()

        # Cloud Percentage
        cloud = image.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()

        # Satellite Date
        date = ee.Date(
            image.get("system:time_start")
        ).format("YYYY-MM-dd").getInfo()

        # Crop Health Score
        health = int(max(0, min(100, round(ndvi_value * 100))))

        # AI Recommendation
        recommendations = []

        if ndvi_value < 0.30:
            recommendations.append("🌱 Poor vegetation detected.")

        elif ndvi_value < 0.60:
            recommendations.append("🟡 Moderate crop health.")

        else:
            recommendations.append("🟢 Healthy vegetation detected.")

        if ndwi_value < 0:
            recommendations.append(
                "💧 Water stress detected. Irrigation recommended."
            )

        else:
            recommendations.append(
                "✅ Adequate soil moisture available."
            )

        if cloud > 30:
            recommendations.append(
                "☁ High cloud cover. Results may be less accurate."
            )

        # Dummy Weather (Later replace with Open-Meteo API)

        weather = {
            "temp": 31,
            "humidity": 68,
            "rain": 0,
            "wind": 11
        }

        return {

            "status": True,

            "ndvi": round(ndvi_value, 3),

            "ndwi": round(ndwi_value, 3),

            "evi": round(evi_value, 3),

            "savi": round(savi_value, 3),

            "cloud_percentage": round(cloud, 2),

            "satellite_date": date,

            "crop_health_score": health,

            "weather": weather,

            "recommendations": recommendations

        }

    except Exception as e:

        return {

            "status": False,

            "message": str(e)

        }