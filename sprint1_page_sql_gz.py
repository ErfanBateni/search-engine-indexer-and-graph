import gzip
import json
import sys

# پارسر ساده‌ی VALUES برای INSERTهای MySQL dump
# ایده: کاراکتر به کاراکتر جلو می‌رویم و رکوردها را به tuple تبدیل می‌کنیم
def iter_mysql_values_tuples(values_part: str):
    """
    ورودی: رشته بعد از VALUES ... تا قبل از ';'
    خروجی: هر رکورد را به صورت لیست از فیلدهای string/None برمی‌گرداند.
    """
    i = 0
    n = len(values_part)

    def skip_ws():
        nonlocal i
        while i < n and values_part[i].isspace():
            i += 1

    while True:
        skip_ws()
        if i >= n:
            return

        # دنبال '('
        if values_part[i] != '(':
            # ممکنه کاما یا چیزای اضافی باشد
            i += 1
            continue
        i += 1  # بعد از '('

        fields = []
        field = ""
        in_str = False
        escape = False

        while i < n:
            ch = values_part[i]

            if in_str:
                if escape:
                    # MySQL dump معمولاً از \ برای escape استفاده می‌کند
                    field += ch
                    escape = False
                else:
                    if ch == "\\":
                        escape = True
                    elif ch == "'":
                        in_str = False
                    else:
                        field += ch
                i += 1
                continue

            # خارج از string
            if ch == "'":
                in_str = True
                i += 1
                continue

            if ch == ",":
                token = field.strip()
                fields.append(None if token.upper() == "NULL" else token)
                field = ""
                i += 1
                continue

            if ch == ")":
                token = field.strip()
                fields.append(None if token.upper() == "NULL" else token)
                i += 1
                break

            field += ch
            i += 1

        yield fields

        # بعد از ) ممکنه , یا ; یا whitespace باشد
        skip_ws()
        if i < n and values_part[i] == ",":
            i += 1
            continue
        # اگر ; باشد یا پایان رشته، تمام
        return


def parse_page_sql_gz(input_path: str, output_path: str, limit: int | None = None):
    """
    از فایل page.sql.gz رکوردهای جدول page را می‌خواند و خروجی JSONL می‌نویسد.
    فیلدهای مورد نیاز:
      page_id (index 0)
      page_namespace (index 1)
      page_title (index 2)
      page_is_redirect (index 4)
    """
    written = 0

    with gzip.open(input_path, "rt", encoding="utf-8", errors="replace") as f_in, \
            open(output_path, "w", encoding="utf-8") as f_out:

        for line in f_in:
            # فقط INSERTهای جدول page مهمه
            if not line.startswith("INSERT INTO `page` VALUES "):
                continue

            # بخش VALUES را جدا کن
            # نمونه: INSERT INTO `page` VALUES (...),(...);
            prefix = "INSERT INTO `page` VALUES "
            values_part = line[len(prefix):].rstrip()

            # اگر خط چندخطی باشد (کمتر رایجه ولی ممکنه)، ادامه را جمع کن تا ; بیاد
            while not values_part.endswith(";"):
                nxt = next(f_in, "")
                if not nxt:
                    break
                values_part += nxt.rstrip()

            # حذف ; انتهایی
            if values_part.endswith(";"):
                values_part = values_part[:-1]

            # parse tuples
            for fields in iter_mysql_values_tuples(values_part):
                # محافظت: حداقل 5 فیلد لازم داریم
                if len(fields) < 5:
                    continue

                try:
                    page_id = int(fields[0]) if fields[0] is not None else None
                    page_namespace = int(fields[1]) if fields[1] is not None else 0
                    page_title = fields[2] or ""
                    page_is_redirect = int(fields[4]) if fields[4] is not None else 0
                except ValueError:
                    continue

                if page_id is None:
                    continue

                rec = {
                    "id": page_id,
                    "ns": page_namespace,
                    "title": page_title,
                    "redirect": page_is_redirect
                }
                f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1

                if written % 200000 == 0:
                    print(f"written: {written}", file=sys.stderr)

                if limit is not None and written >= limit:
                    print(f"done. total written: {written}", file=sys.stderr)
                    return

    print(f"done. total written: {written}", file=sys.stderr)


if __name__ == "__main__":
    input_path = r"E:\Dars\Term 9\Data structures and algorithms\Project\data\enwiki-latest-page.sql.gz"
    output_path = r"E:\Dars\Term 9\Data structures and algorithms\Project\out\page_meta.jsonl"
    parse_page_sql_gz(input_path, output_path, limit=10000)
