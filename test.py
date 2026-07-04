from gee import get_latest_image

polygon = [
    [76.7605, 19.2674],
    [76.7610, 19.2674],
    [76.7610, 19.2679],
    [76.7605, 19.2679],
    [76.7605, 19.2674]
]

image = get_latest_image(polygon)

if image:
    print("✅ Image Found")
    print(image.get("PRODUCT_ID").getInfo())
else:
    print("❌ No Image Found")