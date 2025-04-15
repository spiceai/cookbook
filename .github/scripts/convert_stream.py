import json
import sys

def extract_contents(file_path):
    contents = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("data: "):
                json_part = line[len("data: "):]
                if json_part:
                    try:
                        data = json.loads(json_part)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            contents.append(content)
                    except json.JSONDecodeError:
                        continue
    return "".join(contents)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_stream.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    content = extract_contents(input_file)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Extracted content written to {output_file}")
