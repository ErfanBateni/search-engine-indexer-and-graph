import bz2
import json
import sys
import xml.etree.ElementTree as ET


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def parse_bz2_xml(input_path: str, output_path: str, limit: int | None = None):
    count = 0

    with bz2.open(input_path, "rb") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
        context = ET.iterparse(f_in, events=("end",))

        for event, elem in context:
            if strip_ns(elem.tag) != "page":
                continue

            title = ""
            page_id = None
            text = ""

            # <page> children: title, ns, id, revision, ...
            for child in list(elem):
                tag = strip_ns(child.tag)

                if tag == "title":
                    title = child.text or ""

                elif tag == "id" and page_id is None:
                    # اولین id داخل page همون page_id است
                    page_id = child.text

                elif tag == "revision":
                    # داخل revision دنبال text می‌گردیم
                    for rchild in list(child):
                        if strip_ns(rchild.tag) == "text":
                            text = rchild.text or ""
                            break

            # فیلتر حداقلی: متن خالی رو رد کن
            if page_id is not None and text:
                rec = {"id": int(page_id), "title": title, "text": text}
                f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1

                if count % 1000 == 0:
                    print(f"written: {count}", file=sys.stderr)

                if limit is not None and count >= limit:
                    break

            # آزادسازی حافظه
            elem.clear()

    print(f"done. total written: {count}", file=sys.stderr)


if __name__ == "__main__":
    input_path = r"E:\Dars\Term 9\Data structures and algorithms\Project\data\enwiki-latest-pages-articles-multistream1.xml-p1p41242.bz2"
    output_path = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\wiki_docs.jsonl"

    parse_bz2_xml(input_path, output_path)
    