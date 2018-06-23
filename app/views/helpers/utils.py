import cStringIO
import csv


def to_csv(data, fieldnames):
    output = cStringIO.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    contents = output.getvalue()
    output.close()

    return contents
