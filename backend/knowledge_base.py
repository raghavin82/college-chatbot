import json

JSON_PATH = "data/processed/semester_3.json"


def load_knowledge_base():
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data

def search_course(query, data):
    query = query.lower()

    results = []

    for course in data["courses"]:
        course_code = course["course_code"].lower()
        course_name = course["course_name"].lower()

        # Search course code/name
        if query in course_code or query in course_name:
            results.append({
                "course_code": course["course_code"],
                "course_name": course["course_name"],
                "module": None,
                "topic": None
            })
            continue

        # Search module topics
        if "modules" in course:
            for module_index, module in enumerate(course["modules"], start=1):

                if "topics" not in module:
                    continue

                for topic in module["topics"]:
                    if query in topic.lower():
                        results.append({
                            "course_code": course["course_code"],
                            "course_name": course["course_name"],
                            "module": module_index,
                            "topic": topic
                        })

    return results


def create_chunks(data):
    chunks = []

    for course in data["courses"]:
        if "modules" not in course:
            continue

        for module_index, module in enumerate(course["modules"], start=1):
            if "topics" not in module:
                continue

            for topic in module["topics"]:
                chunk = {
                    "id": len(chunks) + 1,
                    "course_code": course["course_code"],
                    "course_name": course["course_name"],
                    "module": module_index,
                    "topic": topic
                }

                chunks.append(chunk)

    return chunks


def save_chunks(chunks):
    output_path = "data/processed/chunks.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json. dump(chunks, file, indent=4, ensure_ascii=False)

    print(f"Chunks saved to {output_path}")

if __name__ == "__main__":
    data = load_knowledge_base()

    chunks = create_chunks(data)

    print(f"Total chunks created: {len(chunks)}")

    save_chunks(chunks)

    print("\nFirst 5 chunks:")
    for chunk in chunks[:5]:
        print(chunk)