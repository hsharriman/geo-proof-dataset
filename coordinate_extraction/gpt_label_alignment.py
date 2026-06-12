import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        print("encoded image successfully")
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_label_alignment(coordinates, image_path):
    print("0")
    with open("prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()
    print("1")

    base64_image = encode_image(image_path)
    print("2")
    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "text",
                        "text": f"list of coordinates: {coordinates} \ngeometry diagram: ",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from extract_coordinates import extract_coordinates
    from draw_figures import plot_points

    IMAGE_PATH = "diagram_sample_image/photo5.jpg"
    coordinates = extract_coordinates(IMAGE_PATH)
    print("There are ", len(coordinates), "points")
    print(coordinates)

    labeled_coordinates = get_label_alignment(coordinates, IMAGE_PATH)

    print(labeled_coordinates)
    plot_points(coordinates, f"Extracted Coordinates ({len(coordinates)} points)")
