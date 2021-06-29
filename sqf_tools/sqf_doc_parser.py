import os
import click
import jinja2


class SqfDocGenerator:

    def __init__(self, path):
        self.parent = path
        self.root = path
        self.root_folder = self.root.split('/')[-1]
        self.root_len = len(self.root) + 1
        self.path = path
        self.product_data = {}

    def collect(self):
        self.collect_path(self.path)

    def collect_path(self, path):
        for file in os.listdir(path):
            if file != '.git':
                file_actual = os.path.join(path, file)
                if os.path.isdir(file_actual):
                    self.collect_path(file_actual)

                else:
                    if file_actual.endswith('.sqf'):
                        self.parse_file(file_actual)

    def parse_file(self, file_actual):
        comment_lines = self.extract_doc_comment(file_actual)

        path_parts = self.sanitize_and_split_path(file_actual)

        if comment_lines:
            comment_string = "\n".join(comment_lines)
            self.save_meta(path_parts, comment_string)

    def extract_doc_comment(self, file_actual):
        with open(file_actual, 'r') as file:
            product = []
            save_meta = False
            for line in file.readlines():
                # line = line.strip()
                if line.startswith("/*"):
                    save_meta = True
                elif line.startswith("*/"):
                    save_meta = False
                    return product
                else:
                    if save_meta:
                        if line != '':
                            product.append(line)

    def sanitize_and_split_path(self, file_actual):
        path_str = file_actual[self.root_len:]
        path_parts = path_str.split(os.sep)
        return path_parts

    def save_meta(self, parts, comment):
        print(f"save_meta : {parts}")
        keys = parts[:-1]
        filename = parts[-1]

        data = self.locate_key_path(keys, self.product_data)
        data[filename] = {}
        data[filename]['comment'] = comment

    def locate_key_path(self, keys, data_dict):
        key_path = "/".join(keys)
        print(key_path)
        if key_path not in data_dict.keys():
            data_dict[key_path] = {}
        return data_dict[key_path]

    def report(self, output="report.html"):
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template("report_template.html")
        outputText = template.render(
            data=self.product_data,
            root=self.root_folder
        )
        with open(output, 'w') as report_file:
            report_file.write(outputText)


@click.command()
@click.argument(
    'path',
)
@click.argument(
    'output'
)
def main(path, output):

    sdg = SqfDocGenerator(path)
    sdg.collect()
    sdg.report(output)


if __name__ == '__main__':
    main()
